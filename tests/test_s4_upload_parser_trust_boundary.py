from io import BytesIO
from unittest.mock import patch
import zipfile

import pytest

from core.file_handler import FileHandler
from utils.error_handler import FileError


class Upload(BytesIO):
    def __init__(self, name, data, size=None):
        super().__init__(data)
        self.name = name
        self.size = len(data) if size is None else size


def _ooxml_bytes(required_member):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types />")
        archive.writestr(required_member, "<document />")
    return buffer.getvalue()


def _minimal_pdf():
    return (
        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"
        b"trailer\n<< /Root 1 0 R >>\n%%EOF\n"
    )


@pytest.mark.parametrize("payload", [b"not a PDF", b"%PDF-1.4\nmissing trailer"])
def test_mismatched_or_malformed_pdf_bytes_are_rejected_before_parser_dispatch(payload):
    upload = Upload("mismatch.pdf", payload)

    with patch.object(FileHandler, "_process_file", return_value="parser reached") as parser:
        result = FileHandler.handle([upload])

    assert parser.called is False
    assert result["files"] == [{"filename": "mismatch.pdf", "error": "Invalid or mismatched binary file"}]


def test_valid_pdf_candidate_reaches_parser_dispatch():
    upload = Upload("valid.pdf", _minimal_pdf())

    with patch.object(FileHandler, "_process_file", return_value="parsed") as parser:
        result = FileHandler.handle([upload])

    parser.assert_called_once()
    assert result["files"][0]["content"] == "parsed"


@pytest.mark.parametrize(
    ("filename", "payload"),
    [
        ("legacy.xls", b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"),
        ("image.png", b"\x89PNG\r\n\x1a\nvalid"),
    ],
)
def test_valid_legacy_excel_and_image_signatures_reach_dispatch(filename, payload):
    upload = Upload(filename, payload)

    with patch.object(FileHandler, "_process_file", return_value="parsed") as parser:
        FileHandler.handle([upload])

    parser.assert_called_once()


@pytest.mark.parametrize(
    ("filename", "required_member"),
    [
        ("sheet.xlsx", "xl/workbook.xml"),
        ("document.docx", "word/document.xml"),
        ("slides.pptx", "ppt/presentation.xml"),
    ],
)
def test_valid_ooxml_candidate_reaches_parser_dispatch(filename, required_member):
    upload = Upload(filename, _ooxml_bytes(required_member))

    with patch.object(FileHandler, "_process_file", return_value="parsed") as parser:
        FileHandler.handle([upload])

    parser.assert_called_once()


def test_zip_without_expected_ooxml_structure_is_rejected_before_parser_dispatch():
    upload = Upload("mismatch.docx", _ooxml_bytes("xl/workbook.xml"))

    with patch.object(FileHandler, "_process_file", return_value="parser reached") as parser:
        result = FileHandler.handle([upload])

    assert parser.called is False
    assert result["files"][0]["error"] == "Invalid or mismatched binary file"


def test_image_extension_mismatch_does_not_reach_provider():
    upload = Upload("mismatch.png", b"not an image")
    gemini_agent = object()

    with patch.object(FileHandler, "_process_file", return_value="provider reached") as processor:
        FileHandler.handle([upload], gemini_agent)

    processor.assert_not_called()


def test_direct_filehandler_invocation_applies_binary_validation():
    upload = Upload("mismatch.pptx", b"not a zip container")

    result = FileHandler.handle([upload])

    assert result["files"][0]["error"] == "Invalid or mismatched binary file"


def test_existing_file_count_and_size_limits_remain_enforced():
    uploads = [Upload(f"file-{index}.txt", b"ok") for index in range(FileHandler.MAX_FILES + 1)]
    with pytest.raises(FileError):
        FileHandler.handle(uploads)

    oversized = Upload("large.pdf", _minimal_pdf(), size=FileHandler.MAX_SIZE + 1)
    with patch.object(FileHandler, "_process_file") as parser:
        result = FileHandler.handle([oversized])

    parser.assert_not_called()
    assert result["files"][0]["error"] == "File too large (max 10MB)"
