"""
Unit tests for UnixPathMatcher and pattern normalization.
"""

from pathlib import Path
import pytest

from devtul.core.path_matcher import (
    UnixPathMatcher,
    matches_unix_pattern,
    normalize_pattern,
)


def test_normalize_pattern_cross_platform(tmp_path):
    assert normalize_pattern(".\\tests\\foo.py") == "tests/foo.py"
    assert normalize_pattern("./tests/foo.py") == "tests/foo.py"
    assert normalize_pattern("tests\\sub\\file.txt") == "tests/sub/file.txt"
    assert normalize_pattern("'tests/'") == "tests/"
    assert normalize_pattern('"tests/"') == "tests/"

    # Absolute path normalized relative to root_path
    root = tmp_path / "repo"
    root.mkdir()
    target = root / "src" / "main.py"
    norm = normalize_pattern(str(target), root_path=root)
    assert norm == "src/main.py"


def test_matcher_exact_windows_path():
    matcher = UnixPathMatcher([r".\tests\test_migration_and_paths.py"])
    matched, pat, reason = matcher.matches("tests/test_migration_and_paths.py")
    assert matched is True
    assert "exact match" in reason


def test_matcher_directory_trailing_slash():
    matcher = UnixPathMatcher(["tests/"])
    matched, pat, reason = matcher.matches("tests/sub/test_foo.py")
    assert matched is True
    assert "directory path match" in reason

    matched2, _, _ = matcher.matches("src/main.py")
    assert matched2 is False


def test_matcher_bare_directory_component():
    matcher = UnixPathMatcher(["tests"])
    matched, pat, reason = matcher.matches("tests/test_foo.py")
    assert matched is True
    assert "directory component matched" in reason

    matched_sub, _, _ = matcher.matches("sub/tests/nested.py")
    assert matched_sub is True

    matched_other, _, _ = matcher.matches("src/main.py")
    assert matched_other is False


def test_matcher_wildcard_patterns():
    matcher = UnixPathMatcher(["*test*", "*.py"])
    matched_dir, _, _ = matcher.matches("tests/test_foo.py")
    assert matched_dir is True

    matched_file, _, _ = matcher.matches("src/devtul/main.py")
    assert matched_file is True

    matched_md, _, _ = matcher.matches("README.md")
    assert matched_md is False


def test_matcher_globstar():
    matcher = UnixPathMatcher(["src/**/*.py"])
    assert matcher.matches("src/devtul/commands/tree.py")[0] is True
    assert matcher.matches("src/main.py")[0] is True
    assert matcher.matches("tests/test_main.py")[0] is False


def test_debug_callback_logging():
    logs = []
    matcher = UnixPathMatcher(
        ["tests/"],
        debug_callback=lambda msg: logs.append(msg),
    )
    matcher.matches("tests/test_foo.py")
    assert len(logs) == 1
    assert "[DEBUG] Path 'tests/test_foo.py' matched" in logs[0]


def test_matches_unix_pattern_helper():
    assert matches_unix_pattern("tests/foo.py", "tests/") is True
    assert matches_unix_pattern("src/main.py", "tests/") is False
    assert matches_unix_pattern(Path("tests/bar.py"), "tests") is True
