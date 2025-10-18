"""
Scan command for devtul - lists all files in a directory (not just git tracked).
"""

from pathlib import Path
from typing import List, Optional

import typer

from ..core.file_utils import get_all_files

from ..core import (
    IGNORE_PARTS,
    IGNORE_PATTERNS,
    apply_filters,
    build_tree_structure,
    process_paths_for_subdir,
    write_output,
)


def scan(
    path: Path = typer.Argument(
        Path().cwd().resolve(), help="Path to the directory to scan"
    ),
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
    tree_format: bool = typer.Option(
        False, "--tree", help="Output as tree structure instead of list"
    ),
):
    """
    Scan and list all files in a directory (not just git tracked).

    This command recursively scans a directory and lists all files, using
    ignore patterns to skip common build artifacts, caches, and other files
    that are typically not interesting for documentation or analysis.

    Examples:
        scan ./my-project
        scan ./my-project --match "*.py" --print
        scan ./my-project --sub-dir src --tree -f files_tree.txt
        scan ./my-project --exclude "*.log" --exclude "*.tmp"
    """
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    if not path.is_dir():
        typer.echo(f"Error: {path} is not a directory", err=True)
        raise typer.Exit(1)

    # Get all files using ignore patterns
    all_files = get_all_files(path, IGNORE_PARTS, IGNORE_PATTERNS)

    # Process for sub-directory if provided
    _, adjusted_files = process_paths_for_subdir(all_files, sub_dir)

    # Apply match/exclude filters
    filtered_files = apply_filters(adjusted_files, match, exclude)

    if not filtered_files:
        typer.echo("No files match the specified criteria", err=True)
        raise typer.Exit(1)

    # Format output
    if tree_format:
        output = build_tree_structure(filtered_files)
    else:
        output = "\n".join(sorted(filtered_files))

    # Determine output behavior
    should_print = print_output or (file is None)

    # Write output
    write_output(output, file, encoding, should_print)
