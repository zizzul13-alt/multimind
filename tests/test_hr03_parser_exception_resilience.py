import sys
import types
from io import BytesIO
from unittest.mock import patch

import pytest

import app
from core.file_handler import FileHandler


class Upload(BytesIO):
    def __init__(self, name, data=b"content"):
        super().__init__(data)
        self.name = name
        self.size = len(data)


class FakePage:
    def __init__(self, text):
        self.text = text

    def extract_text(self):
        return self.text


class FailingPdfPlumber:
    @staticmethod
    def open(file):
        raise RuntimeError("primary parser internal path /secret")


def _valid_binary(*args, **kwargs):
    return True


def _result_for(upload, gemini_agent=None):
    with patch.object(FileHandler, "_is_valid_binary_candidate", _valid_binary):
        return FileHandler.handle([upload], gemini_agent)


def test_pdf_primary_failure_uses_pypdf2_fallback(monkeypatch):
    class Reader:
        pages = [FakePage("fallback text")]

    monkeypatch.setitem(sys.modules, "pdfplumber", FailingPdfPlumber)
    monkeypatch.setitem(sys.modules, "PyPDF2", types.SimpleNamespace(PdfReader=lambda file: Reader()))

    result = _result_for(Upload("document.pdf"))

    assert result["files"][0]["content"] == "fallback text\n"


def test_pdf_primary_parser_does_not_catch_keyboard_interrupt(monkeypatch):
    fallback_calls = []

    class InterruptingPdfPlumber:
        @staticmethod
        def open(file):
            raise KeyboardInterrupt("stop parsing")

    monkeypatch.setitem(sys.modules, "pdfplumber", InterruptingPdfPlumber)
    monkeypatch.setitem(
        sys.modules,
        "PyPDF2",
        types.SimpleNamespace(PdfReader=lambda file: fallback_calls.append(file)),
    )

    with pytest.raises(KeyboardInterrupt):
        _result_for(Upload("document.pdf"))

    assert fallback_calls == []


def test_pdf_both_parser_failures_return_sanitized_error(monkeypatch):
    def fail_fallback(file):
        raise RuntimeError("fallback parser internal path /secret")

    monkeypatch.setitem(sys.modules, "pdfplumber", FailingPdfPlumber)
    monkeypatch.setitem(sys.modules, "PyPDF2", types.SimpleNamespace(PdfReader=fail_fallback))

    result = _result_for(Upload("document.pdf"))

    error = result["files"][0]["error"]
    assert error == FileHandler.PARSER_ERROR_MESSAGES["pdf"]
    assert "secret" not in error
    assert "fallback parser" not in error


def test_pypdf2_none_text_is_skipped_and_returns_no_text(monkeypatch):
    class Reader:
        pages = [FakePage(None), FakePage("")]

    monkeypatch.setitem(sys.modules, "pdfplumber", FailingPdfPlumber)
    monkeypatch.setitem(sys.modules, "PyPDF2", types.SimpleNamespace(PdfReader=lambda file: Reader()))

    result = _result_for(Upload("document.pdf"))

    assert result["files"][0]["content"] == "No text found in PDF"


def test_excel_parser_exception_is_sanitized():
    with patch("core.file_handler.pd.read_excel", side_effect=RuntimeError("excel internal /secret")):
        result = _result_for(Upload("sheet.xlsx"))

    assert result["files"][0]["error"] == FileHandler.PARSER_ERROR_MESSAGES["excel"]


def test_word_parser_exception_is_sanitized(monkeypatch):
    monkeypatch.setitem(
        sys.modules,
        "docx",
        types.SimpleNamespace(Document=lambda file: (_ for _ in ()).throw(RuntimeError("word internal"))),
    )

    result = _result_for(Upload("document.docx"))

    assert result["files"][0]["error"] == FileHandler.PARSER_ERROR_MESSAGES["word"]


def test_powerpoint_parser_exception_is_sanitized(monkeypatch):
    monkeypatch.setitem(
        sys.modules,
        "pptx",
        types.SimpleNamespace(Presentation=lambda file: (_ for _ in ()).throw(RuntimeError("ppt internal"))),
    )

    result = _result_for(Upload("slides.pptx"))

    assert result["files"][0]["error"] == FileHandler.PARSER_ERROR_MESSAGES["powerpoint"]


def test_image_analysis_exception_is_sanitized():
    class FailingGemini:
        def analyze_image(self, file):
            raise RuntimeError("provider internal path /secret")

    result = _result_for(Upload("image.png"), FailingGemini())

    assert result["files"][0]["error"] == FileHandler.PARSER_ERROR_MESSAGES["image"]


def test_mixed_uploads_retain_success_when_one_parser_fails():
    good = Upload("good.txt", b"usable text")
    bad = Upload("bad.xlsx")

    with patch.object(FileHandler, "_is_valid_binary_candidate", _valid_binary):
        with patch("core.file_handler.pd.read_excel", side_effect=RuntimeError("excel internal")):
            result = FileHandler.handle([good, bad])

    assert result["files"][0]["content"] == "usable text"
    assert result["files"][1]["error"] == FileHandler.PARSER_ERROR_MESSAGES["excel"]


def test_invalid_binary_is_rejected_before_parser_dispatch():
    upload = Upload("invalid.pdf", b"not a PDF")

    with patch.object(FileHandler, "_process_file", return_value="parser reached") as parser:
        result = FileHandler.handle([upload])

    parser.assert_not_called()
    assert result["files"][0]["error"] == "Invalid or mismatched binary file"


def test_process_chat_upload_block_surfaces_errors_and_keeps_content(monkeypatch):
    class SessionState(types.SimpleNamespace):
        def get(self, key, default=None):
            return getattr(self, key, default)

    captured = {}

    class RecordingOrchestrator:
        def __init__(self, **_agents):
            pass

        def debate(self, **kwargs):
            captured.update(kwargs)
            return {
                "status": "success", "final_answer": "usable answer",
                "total_tokens": 1, "total_cost": 0.0,
            }

    warnings = []
    ui = types.SimpleNamespace(
        session_state=SessionState(
            user_id="test-user",
            compressor_enabled=False,
            current_session={"id": "session-1", "mode": "coding"},
            active_agents=["cloudflare"],
            debate_rounds=1,
            selected_skill="default",
            memories={"session-1": types.SimpleNamespace(get_context=lambda: "prior context")},
        ),
        warning=warnings.append,
        error=lambda _message: None,
        success=lambda _message: None,
        rerun=lambda: None,
    )
    agents = {name: None for name in (
        "unified", "remote", "gemini", "deepseek", "groq", "cloudflare",
        "openrouter", "huggingface",
    )}
    agents["cloudflare"] = object()
    parser = patch("core.file_handler.pd.read_excel", side_effect=RuntimeError("internal /secret"))
    monkeypatch.setattr(app, "st", ui)
    monkeypatch.setattr(app, "get_agents", lambda _user_id: agents)
    monkeypatch.setattr(app, "DebateOrchestrator", RecordingOrchestrator)
    monkeypatch.setattr(app, "get_db_manager", lambda _user_id: object())
    monkeypatch.setattr(app, "persist_chat_and_update_memory", lambda *_args: True)

    with patch.object(FileHandler, "_is_valid_binary_candidate", return_value=True), parser as read_excel:
        app.process_chat("prompt", [Upload("good.txt", b"usable"), Upload("bad.xlsx")], "continue")

    read_excel.assert_called_once()
    assert "--- FILE: good.txt ---\nusable" in captured["context"]
    assert "prior context" in captured["context"]
    assert warnings == [f"bad.xlsx: {FileHandler.PARSER_ERROR_MESSAGES['excel']}"]
    assert all("secret" not in warning for warning in warnings)
