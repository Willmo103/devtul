"""
File filtering utilities for devtul.
"""

import fnmatch
from pathlib import Path
from typing import List, Optional


def should_ignore_path(
    path: Path, ignore_parts: List[str], ignore_patterns: List[str]
) -> bool:
    """
    Check if a path should be ignored based on ignore patterns.

    Args:
        path: Path to check
        ignore_parts: List of strings that should not appear anywhere in the path
        ignore_patterns: List of glob patterns to match against the path

    Returns:
        True if the path should be ignored, False otherwise
    """
    path_str = str(path)

    # Check ignore parts (simple substring match)
    for part in ignore_parts:
        if part in path_str:
            return True

    # Check ignore patterns (glob match)
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(path.name, pattern):
            return True

    return False


def path_has_default_ignore_path_part(path: Path) -> bool:
    """
    Check if a path contains any default ignore parts.

    Args:
        path: Path to check
    Returns:
        True if the path contains any default ignore parts, False otherwise
    """
    from devtul.core.constants import IGNORE_PARTS

    return should_ignore_path(path, ignore_parts=IGNORE_PARTS, ignore_patterns=[])


def path_has_default_ignore_pattern(path: Path) -> bool:
    """
    Check if a path matches any default ignore patterns.

    Args:
        path: Path to check
    Returns:
        True if the path matches any default ignore patterns, False otherwise
    """
    from devtul.core.constants import IGNORE_EXTENSIONS

    return should_ignore_path(path, ignore_parts=[], ignore_patterns=IGNORE_EXTENSIONS)


def extension_is_markdown_formattable(file_path: Path) -> bool:
    """
    Check if a file's extension is one of the markdown-formattable types.

    Args:
        file_path: Path to the file
    Returns:
        True if the file's extension is markdown-formattable, False otherwise
    """
    from devtul.core.constants import MARKDOWN_EXTENSIONS

    return file_path.suffix.lower() in MARKDOWN_EXTENSIONS
