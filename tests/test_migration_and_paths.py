"""
Tests for controller-api migration models, path tools, and tree formatting.
"""

from pathlib import Path
from devtul.core.constants import IGNORE_PARTS
from devtul.core.file_utils import (
    build_tree_structure,
    filter_gathered_paths_by_default_ignores,
    filter_gathered_paths_by_path_parts,
    is_git_repo,
)
from devtul.core.models import (
    BaseFileStat,
    BaseTextFile,
    FilePath,
    TextFileLine,
)
from devtul.core.tts import PiperConfig, PiperEngine


def test_is_git_repo(tmp_path):
    repo_root = Path(__file__).resolve().parent.parent
    assert is_git_repo(repo_root) is True
    non_git = tmp_path / "isolated_non_git_folder"
    non_git.mkdir()
    assert is_git_repo(non_git) is False


def test_ignore_parts_excludes_git_but_keeps_gitignore():
    paths = [
        Path("my_project/.git"),
        Path("my_project/.git/HEAD"),
        Path("my_project/.gitignore"),
        Path("my_project/src/main.py"),
        Path("my_project/temp/scratch.txt"),
        Path("my_project/template.py"),
    ]
    filtered = filter_gathered_paths_by_path_parts(paths, IGNORE_PARTS)
    names = [p.name for p in filtered]

    assert ".gitignore" in names
    assert "template.py" in names
    assert "main.py" in names
    assert ".git" not in names
    assert "HEAD" not in names
    assert "scratch.txt" not in names


def test_build_tree_structure_cross_platform():
    files = [
        "src\\devtul\\main.py",
        "src/devtul/commands/tree.py",
        "README.md",
    ]
    tree = build_tree_structure(files)
    assert "├── src/" in tree
    assert "main.py" in tree
    assert "tree.py" in tree
    assert "README.md" in tree


def test_file_path_model():
    p = Path("src/devtul/main.py")
    fp = FilePath.from_path(p)
    assert fp.name == "main.py"
    assert fp.suffix == ".py"
    assert fp.stem == "main"
    assert "main.py" in fp.parts
    assert fp.Path.name == "main.py"


def test_base_file_stat_model():
    p = Path(__file__)
    stat_from_path = BaseFileStat.from_path(p)
    assert stat_from_path.st_size > 0
    st = p.stat()
    stat_model = BaseFileStat.from_stat(st)
    assert stat_model.st_size == stat_from_path.st_size
    iso_dict = stat_model.to_iso_dict()
    assert "st_mtime" in iso_dict
    assert isinstance(iso_dict["st_mtime"], str)


def test_base_text_file_and_lines():
    p = Path(__file__)
    tf = BaseTextFile.from_file(p, read_content=True)
    assert len(tf.lines) > 0
    tf2 = BaseTextFile.from_path(p, read_content=False)
    assert tf2.path.name == p.name
    first_line = tf.lines[0]
    assert isinstance(first_line, TextFileLine)
    assert first_line.line_number == 1


def test_ignore_relative_to_root_in_temp_dir(tmp_path):
    repo = tmp_path / "my_project"
    repo.mkdir()
    (repo / "main.py").write_text("print('hello')")
    (repo / "sub").mkdir()
    (repo / "sub" / "file.txt").write_text("data")
    (repo / "sub" / ".git").mkdir()
    (repo / "sub" / ".git" / "config").write_text("repo")

    paths = [
        repo / "main.py",
        repo / "sub" / "file.txt",
        repo / "sub" / ".git" / "config",
    ]
    filtered = filter_gathered_paths_by_default_ignores(paths, root_path=repo)
    names = [p.name for p in filtered]
    assert "main.py" in names
    assert "file.txt" in names
    assert "config" not in names


def test_piper_engine_config():
    config = PiperConfig(default_model="en_US-lessac-medium", length_scale=1.2)
    engine = PiperEngine(config=config)
    assert engine.config.length_scale == 1.2
    assert engine.model_path.name == "en_US-lessac-medium.onnx"
