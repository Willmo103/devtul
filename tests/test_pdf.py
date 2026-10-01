"""
Tests for PrintPdfCommand ('dt ppdf').
"""

from unittest.mock import MagicMock, patch
import pytest

from devtul.commands.pdf import PrintPdfCommand, parse_page_range


def test_parse_page_range():
    total_pages = 10

    # None or empty returns all 0-indexed pages
    assert parse_page_range(None, total_pages) == list(range(10))
    assert parse_page_range("", total_pages) == list(range(10))

    # Single pages (1-indexed -> 0-indexed)
    assert parse_page_range("1", total_pages) == [0]
    assert parse_page_range("3", total_pages) == [2]

    # Ranges
    assert parse_page_range("1-3", total_pages) == [0, 1, 2]
    assert parse_page_range("8-10", total_pages) == [7, 8, 9]

    # Comma-separated list and ranges
    assert parse_page_range("1,3,5-7", total_pages) == [0, 2, 4, 5, 6]

    # Out of bounds clamping
    assert parse_page_range("9-15", total_pages) == [8, 9]


def test_print_pdf_command_execution(tmp_path):
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 minimal test file")

    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "Page 1 Line A\nPage 1 Line B with TARGET"
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "Page 2 Line C with TARGET\nPage 2 Line D"

    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page1, mock_page2]
    mock_pdf.__enter__.return_value = mock_pdf

    cmd = PrintPdfCommand()

    with patch("pdfplumber.open", return_value=mock_pdf):
        # Test full extraction
        res = cmd.execute(path=pdf_file)
        assert res.total_lines == 4
        assert "Page 1 Line A" in res.lines

        # Test line filtering with lines_with
        res_filter = cmd.execute(path=pdf_file, lines_with="TARGET")
        assert res_filter.total_lines == 2
        assert "Page 1 Line B with TARGET" in res_filter.lines
        assert "Page 2 Line C with TARGET" in res_filter.lines

        # Test sed and head
        res_sed = cmd.execute(path=pdf_file, sed="s/Page/Sheet/g", head=1)
        assert res_sed.total_lines == 1
        assert "Sheet 1 Line A" in res_sed.lines[0]
