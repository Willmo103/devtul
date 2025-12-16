"""
Tree command for devtul - generates tree structures from git repositories.
"""

from pathlib import Path
from typing import List, Optional

import typer

from devtul.core.file_utils import (build_tree_structure, get_all_files,
                                    get_git_files)

from ..core import apply_filters
from ..core.utils import write_to_file


def tree(
    path: Path = typer.Argument(
        Path().cwd().resolve(),
        help="Path to the git repository",
        callback=lambda v: Path(v).resolve(),
    ),
    file: Optional[Path] = typer.Option(None, "-f", "--file", help="Output file path"),
    match: List[str] = typer.Option(
        [],
        "-m",
        "--match",
        help="Pattern to match files (can be used multiple times)",
    ),
    exclude: List[str] = typer.Option(
        [],
        "-e",
        "--exclude",
        help="Pattern to exclude files (overrides match patterns)",
    ),
    include_empty: bool = typer.Option(
        False, "--empty/--no-empty", help="Include empty files"
    ),
    git: bool = typer.Option(
        True, "--git/--no-git", help="Look for git tracked files or all files"
    ),
):
    """
    Generate a tree structure from git tracked files.

    Creates a visual tree representation of all files tracked by git in the specified repository.
    Uses the same tree characters as standard tree commands (├── └── │).

    Examples:
        tree ./my-repo
        tree ./my-repo --match "*.py" --match "*.md" --print
        tree ./my-repo --sub-dir src -f tree_output.txt
    """
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    if not git or not (path / ".git").exists():
        all_files = get_all_files(path, include_empty=include_empty, only_empty=False)
    else:
        # Get git files
        all_files = get_git_files(path, include_empty=include_empty, only_empty=False)

    # Apply match/exclude filters to the adjusted paths
    filtered_files = apply_filters(all_files, match, exclude)

    if not filtered_files:
        typer.echo("No files match the specified criteria", err=True)
        raise typer.Exit(1)

    # Build tree structure using the final filtered and adjusted list
    tree_output = build_tree_structure(filtered_files, parent=path.as_posix())

    # Determine output behavior
    if file is None:
        print(tree_output)
        return
    output_file = file
    if file is not None and file == Path():
        output_file = Path.cwd() / "file_tree.md"

    # Write output
    write_to_file(tree_output, output_file)
