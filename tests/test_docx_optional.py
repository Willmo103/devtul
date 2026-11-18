from pathlib import Path
from unittest.mock import patch
import pytest
from typer.testing import CliRunner

from devtul.core.docx_processor import DocxProcessor
from devtul.main import app

runner = CliRunner()


def test_docx_processor_raises_when_missing():
    with patch("devtul.core.docx_processor.docx", None):
        with pytest.raises(ImportError, match="requires the 'python-docx' library"):
            DocxProcessor.convert_markdown_to_docx("# Hello", Path("dummy.docx"))


def test_repr_command_exits_cleanly_when_docx_missing(tmp_path: Path):
    # Ensure there is at least one file to scan
    sample_file = tmp_path / "main.py"
    sample_file.write_text("print('hello world')")

    with patch("devtul.core.docx_processor.docx", None):
        res = runner.invoke(app, ["rpr", str(tmp_path), "--docx", "--no-git"])
        assert res.exit_code == 1
        assert "requires the 'python-docx' library" in res.output
