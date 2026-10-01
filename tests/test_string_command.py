"""
Tests for StringCommand abstraction and stream filtering pipeline.
"""

import pytest

from devtul.core.command import StringCommand
from devtul.core.models import StringFilterOptions


class ConcreteStringCommand(StringCommand):
    """Concrete subclass for testing."""

    name = "test-str"
    help = "Test string command"

    @property
    def usage(self) -> str:
        return "test-str"

    @property
    def examples(self) -> list[str]:
        return ["test-str"]


@pytest.fixture
def cmd():
    return ConcreteStringCommand()


def test_apply_sed_basic(cmd):
    assert cmd.apply_sed("hello world", "s/world/there/") == "hello there"
    assert cmd.apply_sed("foo foo foo", "s/foo/bar/") == "bar foo foo"


def test_apply_sed_global_flag(cmd):
    assert cmd.apply_sed("foo foo foo", "s/foo/bar/g") == "bar bar bar"


def test_apply_sed_case_insensitive(cmd):
    assert cmd.apply_sed("HELLO world", "s/hello/hi/i") == "hi world"
    assert cmd.apply_sed("HELLO hello HeLLo", "s/hello/hi/gi") == "hi hi hi"


def test_apply_sed_custom_delimiters(cmd):
    assert cmd.apply_sed("path/to/file", "s#path/to/#dest/#") == "dest/file"
    assert cmd.apply_sed("alpha|beta|gamma", "s|beta|omega|") == "alpha|omega|gamma"


def test_apply_sed_invalid(cmd):
    # Should safely return original string
    assert cmd.apply_sed("test string", "") == "test string"
    assert cmd.apply_sed("test string", "invalid") == "test string"
    assert cmd.apply_sed("test string", "s//") == "test string"


def test_process_lines_grep(cmd):
    lines = ["apple", "banana", "cherry", "apricot", "berry"]
    opts = StringFilterOptions(grep=r"^a")
    res = cmd.process_lines(lines, opts)
    assert res == ["apple", "apricot"]


def test_process_lines_lines_with(cmd):
    lines = ["First Line", "Second line with Target", "Third line", "TARGET at start"]
    opts = StringFilterOptions(lines_with="target")
    res = cmd.process_lines(lines, opts)
    assert res == ["Second line with Target", "TARGET at start"]


def test_process_lines_head_and_tail(cmd):
    lines = [f"line-{i}" for i in range(10)]

    opts_head = StringFilterOptions(head=3)
    assert cmd.process_lines(lines, opts_head) == ["line-0", "line-1", "line-2"]

    opts_tail = StringFilterOptions(tail=2)
    assert cmd.process_lines(lines, opts_tail) == ["line-8", "line-9"]

    opts_both = StringFilterOptions(head=5, tail=2)
    # Head first gives lines 0..4, then tail gives lines 3..4
    assert cmd.process_lines(lines, opts_both) == ["line-3", "line-4"]


def test_process_lines_numbered(cmd):
    lines = ["alpha", "beta"]
    opts = StringFilterOptions(numbered=True)
    res = cmd.process_lines(lines, opts)
    assert len(res) == 2
    assert "1" in res[0] and "alpha" in res[0]
    assert "2" in res[1] and "beta" in res[1]


def test_process_lines_combined_pipeline(cmd):
    lines = [
        "error: connection failed",
        "info: service started",
        "error: timeout occurred",
        "error: authentication failed",
        "debug: packet received",
    ]
    opts = StringFilterOptions(
        grep=r"^error:",
        sed="s/failed/RETRY/g",
        head=2,
        numbered=True,
    )
    res = cmd.process_lines(lines, opts)
    assert len(res) == 2
    assert "RETRY" in res[0]
    assert "timeout" in res[1]
