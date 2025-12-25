import fnmatch
import os
import shutil
import subprocess
from os import walk
from pathlib import Path
from typing import List, Optional

import typer

from devtul.core.constants import IGNORE_EXTENSIONS, IGNORE_PARTS, GitScanModes
from devtul.core.models import FileResult, FileResultsModel, FileSearchMatch


def gather_all_paths(root: Path) -> List[Path]:
    """Gather all file and directory paths under the root directory."""
    all_paths = []
    for dirpath, dirnames, filenames in walk(root):
        for dirname in dirnames:
            all_paths.append(Path(dirpath) / dirname)
        for filename in filenames:
            all_paths.append(Path(dirpath) / filename)
    return all_paths


def try_gather_all_git_tracked_paths(repo_path: Path) -> List[Path]:
    """Gather all git-tracked file and directory paths under the repository path."""
    if not repo_path.is_dir() or not repo_path.exists():
        typer.echo(f"Error: {repo_path} is not a valid directory", err=True)
        return []
    elif not any(repo_path.rglob(".git")):
        return gather_all_paths(repo_path)
    tracked_paths = []
    (shell := os.name == "nt")
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "ls-files"],
            capture_output=True,
            text=True,
            check=True,
            shell=shell,
        )
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
        for f in files:
            tracked_paths.append(repo_path / f)
    except subprocess.CalledProcessError as e:
        # check to see if git repo needs to be added as a safe directory
        if "detected dubious ownership" in e.stderr:
            # ask to add repo as safe directory
            typer.echo(
                "Git repository has dubious ownership. Should it be added to the .gitconfig safe.directory list? (y/n): ",
                nl=False,
            )
            choice = input().strip().lower()
            if choice == "y":
                try:
                    subprocess.run(
                        [
                            "git",
                            "config",
                            "--global",
                            "--add",
                            "safe.directory",
                            str(repo_path),
                        ],
                        capture_output=True,
                        text=True,
                        check=True,
                        shell=shell,
                    )
                    typer.echo(f"Added {repo_path} to safe.directory list.")
                    # Retry gathering git tracked paths
                    return try_gather_all_git_tracked_paths(repo_path)
                except subprocess.CalledProcessError as e2:
                    typer.echo(f"Error adding to safe.directory: {e2.stderr}", err=True)
                    return tracked_paths
        typer.echo(f"Error: Unable to get git files from {repo_path}", err=True)
        typer.echo(f"Git error: {e.stderr}", err=True)
        return tracked_paths
    return tracked_paths


def filter_gathered_paths_by_path_parts(
    paths: List[Path], ignore_parts: List[str]
) -> List[Path]:
    """
    Filter gathered paths by ignoring those that contain specified path parts.
    Args:
        paths: List of gathered file and directory paths
        ignore_parts: List of strings that should not appear anywhere in the path
    Returns:
        Filtered list of paths
    """
    filtered_paths = []
    for path in paths:
        if not any(ign in path.as_posix() for ign in ignore_parts):
            filtered_paths.append(path)
    return filtered_paths


def filter_gathered_paths_by_patterns(
    paths: List[Path], ignore_patterns: List[str]
) -> List[Path]:
    """
    Filter gathered paths by ignoring those that match specified glob patterns.
    Args:
        paths: List of gathered file and directory paths
        ignore_patterns: List of glob patterns to match against the path
    Returns:
        Filtered list of paths
    """
    filtered_paths = []
    for path in paths:
        if not any(fnmatch.fnmatch(path.name, pattern) for pattern in ignore_patterns):
            filtered_paths.append(path)
    return filtered_paths


def filter_gathered_paths_dy_default_ignores(
    paths: List[Path],
) -> List[Path]:
    """
    Filter gathered paths by ignoring those that match default ignore parts and patterns.
    Args:
        paths: List of gathered file and directory paths
    Returns:
        Filtered list of paths
    """
    paths = filter_gathered_paths_by_path_parts(paths, IGNORE_PARTS)
    paths = filter_gathered_paths_by_patterns(paths, IGNORE_EXTENSIONS)
    return paths


def filter_paths_for_empty_folders(
    paths: List[Path],
) -> tuple[List[Path], List[Path]]:
    """
    Filter paths into empty folders and non-empty folders.
    Args:
        paths: List of gathered file and directory paths
    Returns:
        Tuple of (non-empty paths, empty folder paths)
    """
    non_empty_paths = []
    empty_folder_paths = []
    folder_contents = {}

    for path in paths:
        parent = path.parent
        if parent not in folder_contents:
            folder_contents[parent] = []
        folder_contents[parent].append(path)

    for path in paths:
        if path.is_dir():
            if path in folder_contents and len(folder_contents[path]) == 0:
                empty_folder_paths.append(path)
            else:
                non_empty_paths.append(path)
        else:
            non_empty_paths.append(path)

    return non_empty_paths, empty_folder_paths


def filter_paths_for_empty_files(
    paths: List[Path],
) -> tuple[List[Path], List[Path]]:
    """
    Filter paths into empty files and non-empty files.
    Args:
        paths: List of gathered file and directory paths
    Returns:
        Tuple of (non-empty file paths, empty file paths)
    """
    non_empty_file_paths = []
    empty_file_paths = []

    for path in paths:
        if path.is_file():
            if path.stat().st_size == 0:
                empty_file_paths.append(path)
            else:
                non_empty_file_paths.append(path)

    return non_empty_file_paths, empty_file_paths


def prompt_on_git_folder_detection(path: Path) -> str:
    """
    Prompt the user for action when a git folder is detected.
    Args:
        path: Path where the git folder was detected
    Returns:
        User's GitScanModes choice
    """
    typer.echo(f"Git repository detected at {path}. and no --git option was provided.")
    typer.echo("Choose how to proceed:")
    typer.echo("1) Scan using git tracked files only")
    typer.echo("2) Scan all files, ignoring git")
    typer.echo("3) Cancel operation")
    choice = input("Enter your choice (1/2/3): ").strip()
    if choice == "1":
        return GitScanModes.GIT_TRACKED
    elif choice == "2":
        return GitScanModes.ALL_FILES


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


def build_tree_structure(files: List[str], parent: str = ".") -> str:
    """Build a tree structure string from a list of file paths."""
    if not files:
        return ""

    # Build directory structure
    tree_dict = {}
    for file_path in sorted(files):
        parts = file_path.split("/")
        current = tree_dict

        for i, part in enumerate(parts):
            if i == len(parts) - 1:  # It's a file
                if "__files__" not in current:
                    current["__files__"] = []
                current["__files__"].append(part)
            else:  # It's a directory
                if part not in current:
                    current[part] = {}
                current = current[part]

    # Convert tree_dict to tree string
    def render_tree(node: dict, prefix: str = "", is_last: bool = True) -> List[str]:
        lines = []

        # Collect directories
        dirs = [
            (k, v) for k, v in node.items() if k != "__files__" and isinstance(v, dict)
        ]
        dirs.sort(key=lambda x: x[0])

        # Collect files
        files = node.get("__files__", [])
        files.sort()

        # Combine directories and files
        all_items = [(name, "dir", content) for name, content in dirs] + [
            (name, "file", None) for name in files
        ]

        for i, (name, item_type, content) in enumerate(all_items):
            is_last_item = i == len(all_items) - 1

            if item_type == "dir":
                symbol = "└── " if is_last_item else "├── "
                lines.append(f"{prefix}{symbol}{name}/")

                next_prefix = prefix + ("    " if is_last_item else "│   ")
                lines.extend(render_tree(content, next_prefix, is_last_item))
            else:
                symbol = "└── " if is_last_item else "├── "
                lines.append(f"{prefix}{symbol}{name}")

        return lines

    if not tree_dict:
        return ""

    # Start with root directory
    first_line = f"{parent}/"
    root_lines = [first_line]
    if len(tree_dict) == 1 and "__files__" not in tree_dict:
        # Single root directory
        root_name = list(tree_dict.keys())[0]
        root_lines.append(f"{root_name}/")
        root_lines.extend(render_tree(tree_dict[root_name], "   "))
    else:
        # Multiple items at root or files at root
        root_lines.extend(render_tree(tree_dict))

    return "\n".join(root_lines)


def search_in_file(file_path: Path, search_term: str) -> List[FileSearchMatch]:
    """Search for a term in a file and return matching lines with context."""
    matches = []
    try:
        with open(file_path, "r", encoding="utf8", errors="replace") as f:
            for line_num, line in enumerate(f, 1):
                if search_term.lower() in line.lower():
                    matches.append(
                        FileSearchMatch(
                            file_path=file_path.resolve().as_posix(),
                            line_number=line_num,
                            content=line.strip(),
                            file=str(file_path),
                        )
                    )
    except Exception as e:
        matches.append(
            FileSearchMatch(
                file_path=file_path.resolve().as_posix(),
                line_number=0,
                content=f"Error reading file: {e}",
                file=str(file_path),
            )
        )
    return matches


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
