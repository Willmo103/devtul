"""
Tree command for devtul - generates tree structures from git repositories.
"""

from pathlib import Path
from typing import List, Optional

import typer

from ..core import (
    apply_filters,
    build_tree_structure,
    get_git_files,
    process_paths_for_subdir,
    write_output,
)


def tree(
    path: Path = typer.Argument(Path().pwd(), help="Path to the git repository"),
    print_output: bool = typer.Option(
        False, "-p", "--print", help="Print output to STDOUT"
    ),
    encoding: str = typer.Option(
        "utf8",
        "--encoding",
        help="Character encoding to use",
        callback=lambda v: (
            v
            if v in ["utf8", "ascii", "utf16", "latin1"]
            else typer.BadParameter("Invalid encoding")
        ),
    ),
    file: Optional[Path] = typer.Option(None, "-f", "--file", help="Output file path"),
    sub_dir: Optional[str] = typer.Option(
        None, "--sub-dir", help="Specify a sub-directory to treat as the root"
    ),
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

    if not (path / ".git").exists():
        all_files = get_all_filess(path, include_empty=include_empty)
    # Get git files
    all_files = get_git_files(path, include_empty)

    # Process for sub-directory if provided, giving us adjusted paths for display/filtering
    _, adjusted_files = process_paths_for_subdir(all_files, sub_dir)

    # Apply match/exclude filters to the adjusted paths
    filtered_files = apply_filters(adjusted_files, match, exclude)

    if not filtered_files:
        typer.echo("No files match the specified criteria", err=True)
        raise typer.Exit(1)

    # Build tree structure using the final filtered and adjusted list
    tree_output = build_tree_structure(filtered_files)

    # Determine output behavior
    should_print = print_output or (file is None)
    output_file = file
    if file is not None and file == Path():
        output_file = Path.cwd() / "flattened_repo.md"

    # Write output
    write_output(tree_output, output_file, encoding, should_print)
