import fnmatch
from os import walk
from pathlib import Path
from typing import List, Optional

from devtul.core.constants import IGNORE_EXTENSIONS, IGNORE_PARTS
from devtul.core.filters import should_ignore_path


def get_all_files(
    path: Path,
    ignore_parts: Optional[List[str]] = None,
    ignore_patterns: Optional[List[str]] = None,
    include_empty: bool = False,
    only_empty: bool = False,
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
        if path.is_file() and (file_size := path.stat().st_size) is not None:
            if should_ignore_path(
                path, ignore_parts=ignore_parts, ignore_patterns=ignore_patterns
            ):
                continue
            if file_size == 0:
                if only_empty:
                    all_files.append(str(path.relative_to(path.parent.parent)))
                elif not include_empty:
                    continue
                all_files.append(str(path.relative_to(path.parent.parent)))
            else:
                all_files.append(str(path.relative_to(path.parent.parent)))

    return sorted(all_files)


def find_all_dirs_containing_marker_folder(
    root: Path, dir_marker: Optional[str], recurse: bool = False
) -> List[Path]:
    """
    Find all parent directories under root that contain folders matching the marker.

    Args:
        root: Root directory to start the search
        dir_marker: Directory name pattern to look for (e.g., "src")

    Returns:
        List of parent directories (Paths) that contain matching folders
    """
    matching_parents = set()

    for dirpath, dirnames, filenames in walk(root):
        for dirname in dirnames:
            if fnmatch.fnmatch(dirname, dir_marker):
                matching_parents.add((Path(dirpath) / dirname).parent.resolve())
                if not recurse:
                    break  # No need to check other directories in this path

    return sorted(matching_parents)


def find_all_dirs_containing_file(
    root: Path, file_marker: Optional[str], recurse: bool = False
) -> List[Path]:
    """
    Find all directories under root that contain files matching the marker.

    Args:
        root: Root directory to start the search
        file_marker: Filename pattern to look for (e.g., ".gitignore")

    Returns:
        List of directories (Paths) that contain matching files
    """
    matching_dirs = set()

    for dirpath, dirnames, filenames in walk(root):
        for filename in filenames:
            if fnmatch.fnmatch(filename, file_marker):
                matching_dirs.add(Path(dirpath).parent.resolve())
                if not recurse:
                    break  # No need to check other files in this path

    return sorted(matching_dirs)


def get_all_files_from_marked_folders(
    root: Path,
    dir_marker: Optional[str],
    ignore_parts: Optional[List[str]] = None,
    ignore_patterns: Optional[List[str]] = None,
    include_empty: bool = False,
) -> List[str]:
    """
    Get all files from directories under root that contain folders matching the marker.

    Args:
        root: Root directory to start the search
        dir_marker: Directory name pattern to look for (e.g., "src")
        ignore_parts: List of strings that should not appear anywhere in the path
        ignore_patterns: List of glob patterns to match against the path
        include_empty: Whether to include empty files
    Returns:
        An array of MarkedDirectoryResult objects
    """

    all_files = []
    marked_dirs = find_all_dirs_containing_marker_folder(root, dir_marker, recurse=True)

    for marked_dir in marked_dirs:
        files_in_dir = get_all_files(
            marked_dir,
            ignore_parts=ignore_parts,
            ignore_patterns=ignore_patterns,
            include_empty=include_empty,
        )
        all_files.extend(files_in_dir)

    return sorted(all_files)
