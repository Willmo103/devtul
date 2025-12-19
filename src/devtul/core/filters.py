"""
File filtering utilities for devtul.
"""

import fnmatch
from pathlib import Path
from typing import List, Optional


def apply_filters(
    files: List[str], match_patterns: List[str], exclude_patterns: List[str]
) -> List[str]:
    """Apply match and exclude patterns to filter files using set intersection/difference.
    Args:
        files: List of file paths to filter
        match_patterns: List[str], exclude_patterns: List[str]
    Returns:
        List of filtered file paths
    """
    file_set = set(files)

    # Apply match patterns (if any) - only include files that match at least one pattern
    if match_patterns:
        matched_files = set()
        for pattern in match_patterns:
            pattern_matches = {f for f in file_set if fnmatch.fnmatch(f, pattern)}
            matched_files.update(pattern_matches)
        file_set = file_set.intersection(matched_files)

    # Apply exclude patterns - remove files that match any exclude pattern
    if exclude_patterns:
        excluded_files = set()
        for pattern in exclude_patterns:
            pattern_matches = {f for f in file_set if fnmatch.fnmatch(f, pattern)}
            excluded_files.update(pattern_matches)
        file_set = file_set.difference(excluded_files)

    return sorted(list(file_set))


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
