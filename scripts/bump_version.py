#!/usr/bin/env python3
"""
scripts/bump_version.py

Automates semantic version bumping across pyproject.toml and src/devtul/main.py.
Can be executed locally or inside GitHub Actions CI/CD pipelines.

Usage:
    python scripts/bump_version.py show
    python scripts/bump_version.py patch
    python scripts/bump_version.py minor
    python scripts/bump_version.py major
    python scripts/bump_version.py set 0.2.0
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
PYPROJECT_PATH = ROOT_DIR / "pyproject.toml"
MAIN_PY_PATH = ROOT_DIR / "src" / "devtul" / "main.py"
INIT_PY_PATH = ROOT_DIR / "src" / "devtul" / "__init__.py"


def get_current_version(pyproject_path: Path = PYPROJECT_PATH) -> str:
    """Extract the current version string from pyproject.toml."""
    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if not match:
        raise ValueError(f"Could not find version definition in {pyproject_path}")
    return match.group(1)


def parse_semver(version_str: str) -> Tuple[int, int, int, str]:
    """Parse a semver string into (major, minor, patch, prerelease)."""
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?$", version_str.strip())
    if not match:
        raise ValueError(f"Version '{version_str}' is not valid semantic versioning (X.Y.Z[-prerelease])")
    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
    prerelease = match.group(4) or ""
    return major, minor, patch, prerelease


def calculate_next_version(current: str, bump_type: str) -> str:
    """Calculate the next semver version based on bump type."""
    major, minor, patch, _ = parse_semver(current)
    bump = bump_type.lower()
    if bump == "major":
        return f"{major + 1}.0.0"
    elif bump == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Unknown bump type: {bump_type}. Must be 'major', 'minor', or 'patch'.")


def update_pyproject(new_version: str, pyproject_path: Path = PYPROJECT_PATH) -> None:
    """Update version in pyproject.toml."""
    content = pyproject_path.read_text(encoding="utf-8")
    updated, count = re.subn(
        r'^(version\s*=\s*["\'])[^"\']+(["\'])',
        rf"\g<1>{new_version}\g<2>",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if count == 0:
        raise ValueError(f"Failed to replace version in {pyproject_path}")
    pyproject_path.write_text(updated, encoding="utf-8")


def update_source_files(new_version: str, main_py_path: Path = MAIN_PY_PATH, init_py_path: Path = INIT_PY_PATH) -> None:
    """Update static fallback version in main.py and __init__.py if defined."""
    if main_py_path.exists():
        content = main_py_path.read_text(encoding="utf-8")
        updated = re.sub(
            r'(__version__\s*=\s*["\'])[^"\']+(["\'])',
            rf"\g<1>{new_version}\g<2>",
            content,
        )
        main_py_path.write_text(updated, encoding="utf-8")

    if init_py_path.exists():
        content = init_py_path.read_text(encoding="utf-8")
        if "__version__" in content and "=" in content:
            updated = re.sub(
                r'(__version__\s*=\s*["\'])[^"\']+(["\'])',
                rf"\g<1>{new_version}\g<2>",
                content,
            )
            init_py_path.write_text(updated, encoding="utf-8")


def write_github_output(new_version: str) -> None:
    """If running in GitHub Actions, write step outputs to $GITHUB_OUTPUT."""
    gh_output = os.getenv("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"version={new_version}\n")
            f.write(f"tag_name=v{new_version}\n")


def main():
    parser = argparse.ArgumentParser(description="DevTul Version Bumper")
    parser.add_argument(
        "action",
        choices=["show", "patch", "minor", "major", "set"],
        help="Action to perform",
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Explicit version string when using 'set' action",
    )

    args = parser.parse_args()

    current = get_current_version()

    if args.action == "show":
        print(current)
        return

    if args.action == "set":
        if not args.target:
            parser.error("'set' action requires a target version argument (e.g. 'python bump_version.py set 0.2.0')")
        # Validate target
        parse_semver(args.target)
        new_version = args.target
    else:
        new_version = calculate_next_version(current, args.action)

    update_pyproject(new_version)
    update_source_files(new_version)
    write_github_output(new_version)

    print(f"Bumped version from {current} to {new_version}")


if __name__ == "__main__":
    main()
