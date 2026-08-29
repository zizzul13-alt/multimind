import ast
import sys
import types
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

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


def test_process_chat_upload_block_surfaces_errors_and_keeps_content():
    source = Path("app.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    process_chat = next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == "process_chat")
    upload_block = next(
        node for node in process_chat.body
        if isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "uploaded_files"
    )
    function = ast.FunctionDef(
        name="run_upload_block",
        args=ast.arguments(posonlyargs=[], args=[ast.arg(arg="uploaded_files"), ast.arg(arg="gemini")], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
        body=[ast.Assign(targets=[ast.Name(id="file_context", ctx=ast.Store())], value=ast.Constant(value="")), *upload_block.body, ast.Return(value=ast.Name(id="file_context", ctx=ast.Load()))],
        decorator_list=[],
    )
    compiled = ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[]))

    warnings = []
    namespace = {
        "FileHandler": types.SimpleNamespace(handle=lambda files, agent: {"files": [
            {"filename": "good.txt", "content": "usable"},
            {"filename": "bad.pdf", "error": "File could not be read."},
        ]}),
        "st": types.SimpleNamespace(warning=warnings.append),
        "error_logger": types.SimpleNamespace(log=lambda *args, **kwargs: None),
    }
    exec(compile(compiled, "app.py", "exec"), namespace)

    context = namespace["run_upload_block"]([object()], None)

    assert "--- FILE: good.txt ---" in context
    assert "usable" in context
    assert warnings == ["bad.pdf: File could not be read."]
