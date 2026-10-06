"""
Utilities for locating, resolving, and invoking bundled and external developer tools.
"""

from pathlib import Path
import shutil
import subprocess
import sys
from typing import List, Optional

from devtul.core.config import _app_data

BUNDLED_BIN_DIR = _app_data / "bin"


def find_bundled_tool(tool_name: str) -> Optional[Path]:
    """Locate an executable binary in .venv/Scripts, sys.prefix, PATH, or ~/.devtul/bin."""
    # Ensure Windows .exe extension is checked if running on Windows
    names = [tool_name]
    if sys.platform == "win32" and not tool_name.lower().endswith(".exe"):
        names.insert(0, f"{tool_name}.exe")

    # 1. Search virtual environment Scripts
    venv_scripts = Path(sys.prefix) / ("Scripts" if sys.platform == "win32" else "bin")
    for name in names:
        p = venv_scripts / name
        if p.exists() and p.is_file():
            return p

    # 2. Search local devtul bin dir
    for name in names:
        p = BUNDLED_BIN_DIR / name
        if p.exists() and p.is_file():
            return p

    # 3. Search system PATH
    for name in names:
        which = shutil.which(name)
        if which:
            return Path(which)

    return None


def run_bundled_tool(tool_name: str, args: List[str]) -> int:
    """Run a tool binary with given arguments."""
    tool_path = find_bundled_tool(tool_name)
    if not tool_path:
        raise FileNotFoundError(
            f"Tool '{tool_name}' was not found in .venv/Scripts, system PATH, or {BUNDLED_BIN_DIR}."
        )

    cmd = [str(tool_path)] + args
    res = subprocess.run(cmd)
    return res.returncode
