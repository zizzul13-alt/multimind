from io import BytesIO
import sys
import types
import zipfile
from unittest.mock import patch

import pandas as pd
import pytest

from core.file_handler import FileHandler


class Upload(BytesIO):
    def __init__(self, name, data):
        super().__init__(data)
        self.name = name
        self.size = len(data)


OOXML_MEMBERS = {
    "sheet.xlsx": "xl/workbook.xml",
    "document.docx": "word/document.xml",
    "slides.pptx": "ppt/presentation.xml",
}


def _ooxml_bytes(required_member, filler_count=0):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr(required_member, "<document />")
        for index in range(filler_count):
            archive.writestr(f"parts/part-{index}.xml", "")
    return buffer.getvalue()


def _with_declared_uncompressed_total(payload, total):
    """Patch a central-directory field only; no large member body is created."""
    data = bytearray(payload)
    first_central_directory = data.index(b"PK\x01\x02")
    second_central_directory = data.index(b"PK\x01\x02", first_central_directory + 1)
    second_size = int.from_bytes(data[second_central_directory + 24:second_central_directory + 28], "little")
    data[first_central_directory + 24:first_central_directory + 28] = (total - second_size).to_bytes(4, "little")
    return bytes(data)


@pytest.mark.parametrize(("filename", "required_member"), OOXML_MEMBERS.items())
def test_normal_ooxml_candidates_reach_parser(filename, required_member):
    upload = Upload(filename, _ooxml_bytes(required_member))

    with patch.object(FileHandler, "_process_file", return_value="parsed") as parser:
        result = FileHandler.handle([upload])

    parser.assert_called_once()
    assert result["files"][0]["content"] == "parsed"


def test_ooxml_member_count_exactly_at_limit_reaches_parser():
    upload = Upload(
        "sheet.xlsx",
        _ooxml_bytes("xl/workbook.xml", FileHandler.MAX_OOXML_MEMBERS - 2),
    )

    with patch.object(FileHandler, "_process_file", return_value="parsed") as parser:
        FileHandler.handle([upload])

    parser.assert_called_once()


def test_ooxml_member_count_one_over_limit_is_rejected_before_parser():
    upload = Upload(
        "sheet.xlsx",
        _ooxml_bytes("xl/workbook.xml", FileHandler.MAX_OOXML_MEMBERS - 1),
    )

    with patch.object(FileHandler, "_process_file") as parser:
        result = FileHandler.handle([upload])

    parser.assert_not_called()
    assert result["files"] == [{
        "filename": "sheet.xlsx",
        "error": FileHandler.RESOURCE_LIMIT_MESSAGE,
    }]


@pytest.mark.parametrize("declared_total", [100_000_000, 100_000_001])
def test_ooxml_declared_uncompressed_total_boundary(declared_total):
    payload = _with_declared_uncompressed_total(
        _ooxml_bytes("word/document.xml"),
        declared_total,
    )
    upload = Upload("document.docx", payload)

    with patch.object(FileHandler, "_process_file", return_value="parsed") as parser:
        result = FileHandler.handle([upload])

    if declared_total == FileHandler.MAX_OOXML_UNCOMPRESSED_SIZE:
        parser.assert_called_once()
        assert result["files"][0]["content"] == "parsed"
    else:
        parser.assert_not_called()
        assert result["files"][0]["error"] == FileHandler.RESOURCE_LIMIT_MESSAGE


def test_ooxml_resource_preflight_never_reads_member_bodies(monkeypatch):
    upload = Upload("sheet.xlsx", _ooxml_bytes("xl/workbook.xml"))

    def fail_read(*args, **kwargs):
        raise AssertionError("ZIP member body was read")

    monkeypatch.setattr(zipfile.ZipFile, "read", fail_read)
    with patch.object(FileHandler, "_process_file", return_value="parsed") as parser:
        FileHandler.handle([upload])

    parser.assert_called_once()


def test_resource_rejection_does_not_block_successful_sibling():
    rejected = Upload(
        "large.xlsx",
        _ooxml_bytes("xl/workbook.xml", FileHandler.MAX_OOXML_MEMBERS - 1),
    )
    accepted = Upload("usable.txt", b"usable")

    result = FileHandler.handle([rejected, accepted])

    assert result["files"][0]["error"] == FileHandler.RESOURCE_LIMIT_MESSAGE
    assert result["files"][1]["content"] == "usable"


def test_excel_parser_receives_early_row_limit_and_preserves_first_100_rows():
    frame = pd.DataFrame({"value": range(101)})
    upload = Upload("sheet.xlsx", _ooxml_bytes("xl/workbook.xml"))

    with patch("core.file_handler.pd.read_excel", return_value=frame) as reader:
        content = FileHandler._process_file(upload, "excel")

    reader.assert_called_once_with(upload, nrows=100)
    assert "99" in content
    assert "100" not in content


def _install_fake_docx(monkeypatch, document):
    docx = types.ModuleType("docx")
    docx.__path__ = []
    docx.Document = lambda file: document
    text = types.ModuleType("docx.text")
    text.__path__ = []
    paragraph_module = types.ModuleType("docx.text.paragraph")

    class Paragraph:
        def __init__(self, value):
            self.text = value

    paragraph_module.Paragraph = Paragraph
    monkeypatch.setitem(sys.modules, "docx", docx)
    monkeypatch.setitem(sys.modules, "docx.text", text)
    monkeypatch.setitem(sys.modules, "docx.text.paragraph", paragraph_module)
    return Paragraph


def test_word_incremental_extraction_stops_at_budget_and_skips_non_paragraphs(monkeypatch):
    class Document:
        def __init__(self):
            self.visited = 0

        def iter_inner_content(self):
            for item in self.items:
                self.visited += 1
                yield item

    document = Document()
    Paragraph = _install_fake_docx(monkeypatch, document)
    later = Paragraph("later")
    document.items = [Paragraph("x" * 30_000), object(), later]

    content = FileHandler._process_file(Upload("document.docx", b""), "word")

    assert content == "x" * 30_000
    assert document.visited == 1


def test_powerpoint_stops_after_budget_without_visiting_later_shapes_or_slides(monkeypatch):
    class ExhaustingShape:
        text = "x" * 30_000

    class ForbiddenShape:
        @property
        def text(self):
            raise AssertionError("later shape was accessed after the text budget was exhausted")

    class Slide:
        def __init__(self, shapes):
            self.shapes = shapes

    class GuardedSlides:
        def __iter__(self):
            yield Slide([ExhaustingShape(), ForbiddenShape()])
            raise AssertionError("later slide was traversed after the text budget was exhausted")

    presentation = types.SimpleNamespace(slides=GuardedSlides())
    monkeypatch.setitem(sys.modules, "pptx", types.SimpleNamespace(Presentation=lambda file: presentation))

    content = FileHandler._process_file(Upload("slides.pptx", b""), "powerpoint")

    assert content == "x" * 30_000


def test_powerpoint_limits_slide_traversal_to_first_twenty(monkeypatch):
    class Slide:
        def __init__(self, index):
            self.shapes = [types.SimpleNamespace(text=str(index))]

    class GuardedSlides:
        def __init__(self):
            self.visited = []

        def __iter__(self):
            for index in range(1, 21):
                self.visited.append(index)
                yield Slide(index)
            raise AssertionError("slide 21 was traversed")

    slides = GuardedSlides()
    presentation = types.SimpleNamespace(slides=slides)
    monkeypatch.setitem(sys.modules, "pptx", types.SimpleNamespace(Presentation=lambda file: presentation))

    content = FileHandler._process_file(Upload("slides.pptx", b""), "powerpoint")

    assert slides.visited == list(range(1, 21))
    assert "19\n" in content


def test_pdf_text_extraction_stops_after_budget(monkeypatch):
    class Page:
        def __init__(self, text):
            self.text = text
            self.calls = 0

        def extract_text(self):
            self.calls += 1
            return self.text

    pages = [Page("x" * 40_000), Page("later")]

    class Pdf:
        def __init__(self):
            self.pages = pages

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setitem(sys.modules, "pdfplumber", types.SimpleNamespace(open=lambda file: Pdf()))

    content = FileHandler._process_file(Upload("document.pdf", b""), "pdf")

    assert content == "x" * 40_000
    assert pages[0].calls == 1
    assert pages[1].calls == 0
