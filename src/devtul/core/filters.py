"""
File filtering utilities for devtul.
"""

import fnmatch
from pathlib import Path
from typing import List, Optional


def process_paths_for_subdir(
    files: List[str], sub_dir: Optional[str]
) -> tuple[List[str], List[str]]:
    """
    Filters files by a subdirectory and returns both original and adjusted paths.

    This function is key to making the --sub-dir feature work. It takes all the
    files from git, finds the ones inside the target sub-directory, and then
    creates a "virtual" view of them by stripping the sub-directory prefix.
    We need both the original paths (for reading files) and the adjusted paths
    (for display in the tree or list).

    Args:
        files: List of file paths relative to the repo root.
        sub_dir: The subdirectory to filter by, e.g., "src/app".

    Returns:
        A tuple containing:
        - original_paths: Filtered list of original paths (e.g., ['src/app/main.py']).
        - adjusted_paths: Paths adjusted to be relative to the sub_dir (e.g., ['main.py']).
    """
    if not sub_dir:
        return files, files

    # Normalize the path to use forward slashes and remove any leading/trailing ones.
    normalized_dir = sub_dir.strip("/\\").replace("\\", "/")
    if not normalized_dir:
        return files, files

    prefix = normalized_dir + "/"

    # Find all files that start with the subdirectory path.
    original_paths = [f for f in files if f.startswith(prefix)]

    # Create new paths with the subdirectory prefix removed.
    adjusted_paths = [f.removeprefix(prefix) for f in original_paths]

    return original_paths, adjusted_paths


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
