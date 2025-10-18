from devtul.core.constants import IGNORE_EXTENSIONS, IGNORE_PARTS
from devtul.core.filters import should_ignore_path

from typing import List, Optional

from pathlib import Path


def get_all_files(
    path: Path,
    ignore_parts: Optional[List[str]] = None,
    ignore_patterns: Optional[List[str]] = None,
    include_empty: bool = False,
) -> List[str]:
    """
    Get all files in a directory recursively, filtering by ignore patterns.

    Args:
        path: Root directory to search
        ignore_parts: List of strings that should not appear anywhere in the path
        ignore_patterns: List[str] = None: List of glob patterns to match against the path
        include_empty: Whether to include empty files
        subdirs: Optional list of subdirectories to limit the search to

    Returns:
        List of relative file paths (strings)
    """
    all_files = []
    if ignore_parts is None:
        ignore_parts = IGNORE_PARTS
    if ignore_patterns is None:
        ignore_patterns = IGNORE_EXTENSIONS

    for path in path.rglob("*"):
        if path.is_file():
            if should_ignore_path(
                path.relative_to(path), ignore_parts, ignore_patterns
            ):
                continue
            if not include_empty:
                try:
                    if path.stat().st_size == 0:
                        continue
                except Exception:
                    # If we can't check the file, include it anyway
                    pass
            else:
                all_files.append((path.relative_to(path)).replace("\\", "/"))
    return all_files
