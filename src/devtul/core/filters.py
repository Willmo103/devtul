"""
File filtering utilities for devtul.
"""

from pathlib import Path
from typing import Optional

from devtul.core.file_utils import should_ignore_path


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
