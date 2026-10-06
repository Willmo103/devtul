"""
Unit tests for the --fmt-parent / --fmt-root option in tree rendering.
"""

from pathlib import Path
from devtul.core.file_utils import build_tree_structure
from devtul.commands.tree import TreeCommand


def test_build_tree_structure_fmt_parent_true():
    files = ["src/main.py", "README.md"]
    # With fmt_parent=True (default)
    tree_out = build_tree_structure(files, parent="C:/Users/Will/Desktop/scrh", fmt_parent=True)
    first_line = tree_out.splitlines()[0]
    assert first_line == "scrh/"
    assert "src/" in tree_out
    assert "main.py" in tree_out


def test_build_tree_structure_fmt_parent_false():
    files = ["src/main.py", "README.md"]
    # With fmt_parent=False (--fmt-root)
    tree_out = build_tree_structure(files, parent="C:/Users/Will/Desktop/scrh", fmt_parent=False)
    first_line = tree_out.splitlines()[0]
    assert first_line == "C:/Users/Will/Desktop/scrh/"


def test_tree_command_fmt_parent_options(tmp_path):
    sub = tmp_path / "project_root"
    sub.mkdir()
    (sub / "app.py").write_text("print('hi')")

    cmd = TreeCommand()

    # Default fmt_parent=True
    res_default = cmd.execute(path=sub, fmt_parent=True)
    assert res_default is not None
    assert res_default.tree_text.splitlines()[0] == "project_root/"

    # fmt_parent=False (--fmt-root)
    res_root = cmd.execute(path=sub, fmt_parent=False)
    assert res_root is not None
    assert str(sub.resolve().as_posix()) in res_root.tree_text.splitlines()[0]
