"""
Unit tests for command input/output models, FileCommand pipeline, and speech summaries.
"""

from pathlib import Path
import pytest

from devtul.commands.list_files import ListFilesCommand
from devtul.commands.tree import TreeCommand
from devtul.core.command import BaseCommand, FileCommand
from devtul.core.models import (
    CommandResult,
    FileCommandResult,
    FileFilterOptions,
    FilePath,
    FileResult,
    FilterMetrics,
    FindResult,
    ListingResult,
    MarkdownResult,
    TreeResult,
)


class DummyCommand(BaseCommand):
    name = "dummy"
    help = "Dummy command for testing BaseCommand docstring synthesis."

    @property
    def usage(self) -> str:
        return "dt dummy [OPTIONS]"

    @property
    def examples(self) -> list[str]:
        return ["dt dummy --flag", "dt dummy ./path"]


def test_base_command_docstring_synthesis():
    cmd = DummyCommand()
    doc = cmd.get_formatted_help()
    assert "Dummy command for testing BaseCommand docstring synthesis." in doc
    assert "Usage:\n  dt dummy [OPTIONS]" in doc
    assert "Examples:\n  dt dummy --flag\n  dt dummy ./path" in doc


def test_command_result_speech_summary():
    res = CommandResult(command_name="test_cmd")
    summary = res.to_speech_summary()
    assert "Command test_cmd finished successfully" in summary


def test_file_command_result_rendering_and_speech(tmp_path):
    f1 = tmp_path / "file1.txt"
    f1.write_text("hello")
    f2 = tmp_path / "file2.txt"
    f2.write_text("world")

    fr1 = FileResult(f1, tmp_path)
    fr2 = FileResult(f2, tmp_path)

    fcr = FileCommandResult(
        command_name="scan",
        root_path=FilePath.from_path(tmp_path),
        files=[fr1, fr2],
        metrics=FilterMetrics(total_scanned=2, matched_count=2),
    )

    speech = fcr.to_speech_summary()
    assert "DevTul scan processed 2 files in" in speech

    json_str = fcr.render(format="json")
    assert '"command_name": "scan"' in json_str

    yaml_str = fcr.render(format="yaml")
    assert "command_name: scan" in yaml_str


def test_tree_result_speech_and_render(tmp_path):
    tr = TreeResult(
        command_name="tree",
        root_path=FilePath.from_path(tmp_path),
        files=[],
        tree_text="├── src/\n└── main.py",
    )
    assert "DevTul tree rendered 0 files" in tr.to_speech_summary()
    assert tr.render(format="tree") == "├── src/\n└── main.py"


def test_listing_result_formats(tmp_path):
    lr = ListingResult(
        command_name="ls",
        root_path=FilePath.from_path(tmp_path),
        files=[],
        relative_paths=["src/main.py", "tests/test.py"],
    )
    assert "DevTul list found 2 files" in lr.to_speech_summary()
    assert "src/main.py" in lr.render("text")
    assert '"src/main.py"' in lr.render("json")
    assert "path\nsrc/main.py\ntests/test.py" == lr.render("csv")


def test_find_result_speech_and_render(tmp_path):
    fr = FindResult(
        command_name="find",
        root_path=FilePath.from_path(tmp_path),
        files=[],
        term="typer",
        matches=[],
    )
    assert "DevTul find located 0 matches for 'typer'" in fr.to_speech_summary()


def test_file_command_pipeline_in_temp_dir(tmp_path):
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_foo.py").write_text("def test_foo(): pass")
    (tmp_path / "empty.txt").write_text("")

    cmd = TreeCommand()
    options = FileFilterOptions(
        path=tmp_path,
        match=["*.py"],
        exclude=["tests/"],
        git=False,
        include_empty=False,
    )
    results, metrics = cmd.gather_and_filter_files(options)
    names = [r.relative_path.as_posix() for r in results]

    assert "main.py" in names
    assert "tests/test_foo.py" not in names
    assert "empty.txt" not in names
    assert metrics.excluded_count == 1
