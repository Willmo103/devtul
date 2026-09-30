"""
Unit tests for scripts/bump_version.py
"""

import subprocess
import sys
from pathlib import Path
import pytest

from scripts.bump_version import (
    calculate_next_version,
    get_current_version,
    parse_semver,
    update_pyproject,
    update_source_files,
)


def test_parse_semver_valid():
    major, minor, patch, pre = parse_semver("1.2.3")
    assert (major, minor, patch, pre) == (1, 2, 3, "")

    major, minor, patch, pre = parse_semver("0.1.13-alpha.1")
    assert (major, minor, patch, pre) == (0, 1, 13, "alpha.1")


def test_parse_semver_invalid():
    with pytest.raises(ValueError, match="not valid semantic versioning"):
        parse_semver("invalid-version")


def test_calculate_next_version():
    assert calculate_next_version("0.1.13", "patch") == "0.1.14"
    assert calculate_next_version("0.1.13", "minor") == "0.2.0"
    assert calculate_next_version("0.1.13", "major") == "1.0.0"

    with pytest.raises(ValueError, match="Unknown bump type"):
        calculate_next_version("0.1.13", "invalid")


def test_update_files_in_temp_dir(tmp_path):
    pyproj = tmp_path / "pyproject.toml"
    pyproj.write_text('[project]\nname = "test"\nversion = "0.1.13"\n', encoding="utf-8")

    main_py = tmp_path / "main.py"
    main_py.write_text('__version__ = "0.1.13"\nprint(__version__)\n', encoding="utf-8")

    init_py = tmp_path / "__init__.py"
    init_py.write_text('__version__ = "0.1.13"\n', encoding="utf-8")

    assert get_current_version(pyproj) == "0.1.13"

    new_ver = calculate_next_version("0.1.13", "patch")
    update_pyproject(new_ver, pyproject_path=pyproj)
    update_source_files(new_ver, main_py_path=main_py, init_py_path=init_py)

    assert get_current_version(pyproj) == "0.1.14"
    assert '__version__ = "0.1.14"' in main_py.read_text(encoding="utf-8")
    assert '__version__ = "0.1.14"' in init_py.read_text(encoding="utf-8")


def test_cli_show():
    res = subprocess.run(
        [sys.executable, "scripts/bump_version.py", "show"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert res.stdout.strip() == "0.1.13"
