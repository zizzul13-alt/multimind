from io import BytesIO
import struct
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


def _legacy_excel_cfbf(stream_name="Workbook"):
    """Build a minimal CFBF candidate with a named legacy Excel stream."""
    end_of_chain = 0xFFFFFFFE
    fat_sector = 0xFFFFFFFD

    header = bytearray(512)
    header[:8] = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
    struct.pack_into("<H", header, 24, 0x003E)
    struct.pack_into("<H", header, 26, 3)
    header[28:30] = b"\xfe\xff"
    struct.pack_into("<H", header, 30, 9)
    struct.pack_into("<H", header, 32, 6)
    struct.pack_into("<I", header, 44, 1)
    struct.pack_into("<I", header, 48, 0)
    struct.pack_into("<I", header, 60, end_of_chain)
    struct.pack_into("<I", header, 68, end_of_chain)
    struct.pack_into("<I", header, 76, 1)

    directory = bytearray(512)
    root_name = "Root Entry\x00".encode("utf-16le")
    directory[:len(root_name)] = root_name
    struct.pack_into("<H", directory, 64, len(root_name))
    directory[66] = 5
    struct.pack_into("<I", directory, 76, 1)

    workbook_name = f"{stream_name}\x00".encode("utf-16le")
    directory[128:128 + len(workbook_name)] = workbook_name
    struct.pack_into("<H", directory, 192, len(workbook_name))
    directory[194] = 2

    fat = bytearray(512)
    struct.pack_into("<I", fat, 0, end_of_chain)
    struct.pack_into("<I", fat, 4, fat_sector)
    for offset in range(8, 512, 4):
        struct.pack_into("<I", fat, offset, 0xFFFFFFFF)

    return bytes(header + directory + fat)


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


@pytest.mark.parametrize("stream_name", ["Workbook", "Book"])
def test_legacy_excel_workbook_stream_variants_reach_parser_dispatch(stream_name):
    upload = Upload("legacy.xls", _legacy_excel_cfbf(stream_name))

    with patch.object(FileHandler, "_process_file", return_value="parsed") as parser:
        FileHandler.handle([upload])

    parser.assert_called_once()


def test_non_excel_cfbf_renamed_xls_is_rejected_before_parser_dispatch():
    upload = Upload("mismatch.xls", _legacy_excel_cfbf("WordDocument"))

    with patch.object(FileHandler, "_process_file", return_value="parser reached") as parser:
        result = FileHandler.handle([upload])

    parser.assert_not_called()
    assert result["files"] == [{"filename": "mismatch.xls", "error": "Invalid or mismatched binary file"}]


def test_valid_image_signature_reaches_parser_dispatch():
    upload = Upload("image.png", b"\x89PNG\r\n\x1a\nvalid")

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


@pytest.mark.parametrize(
    ("filename", "wrong_member"),
    [
        ("mismatch.docx", "xl/workbook.xml"),
        ("mismatch.xlsx", "word/document.xml"),
    ],
)
def test_ooxml_extension_container_mismatches_are_rejected_before_parser_dispatch(filename, wrong_member):
    upload = Upload(filename, _ooxml_bytes(wrong_member))

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


@pytest.mark.parametrize(
    ("filename", "payload"),
    [
        ("photo.jpg", b"\x89PNG\r\n\x1a\nvalid"),
        ("photo.png", b"\xff\xd8\xffvalid"),
        ("photo.webp", b"GIF89avalid"),
    ],
)
def test_image_signature_extension_mismatches_are_rejected_before_parser_dispatch(filename, payload):
    upload = Upload(filename, payload)

    with patch.object(FileHandler, "_process_file", return_value="parser reached") as parser:
        result = FileHandler.handle([upload])

    parser.assert_not_called()
    assert result["files"] == [{"filename": filename, "error": "Invalid or mismatched binary file"}]


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


def test_exact_max_size_valid_binary_candidate_reaches_parser_dispatch():
    upload = Upload("at-limit.pdf", _minimal_pdf(), size=FileHandler.MAX_SIZE)

    with patch.object(FileHandler, "_process_file", return_value="parsed") as parser:
        result = FileHandler.handle([upload])

    parser.assert_called_once()
    assert result["files"][0]["content"] == "parsed"
