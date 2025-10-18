"""
List files command for devtul - lists git tracked files.
"""

from pathlib import Path
from typing import List, Optional

import typer

from devtul.core.file_utils import get_all_files

from ..core import (
    apply_filters,
    get_git_files,
    process_paths_for_subdir,
    write_output,
)


def ls(
    path: Path = typer.Argument(
        Path().cwd().resolve(), help="Path to the git repository"
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
    sub_dir: Optional[List[str]] = typer.Option(
        None,
        "--sub-dir",
        help="Specify one or more sub-directories to treat as the root",
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
    List git tracked files with optional filtering.

    Behaves like 'git ls-files' but with additional filtering capabilities.
    By default excludes empty files and supports pattern matching.

    Examples:
        ls ./my-repo
        ls ./my-repo --match "*.py" --print
        ls ./my-repo --sub-dir src -f files_list.txt
    """
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    if not (path / ".git").exists():
        all_files = get_all_files(path, include_empty=include_empty)

    # Get git files
    all_files = get_git_files(path, include_empty=include_empty)

    # Apply match/exclude filters
    filtered_files = apply_filters(all_files, match, exclude)

    if not filtered_files:
        typer.echo("No files match the specified criteria", err=True)
        raise typer.Exit(1)

    # Create output
    output = "\n".join(sorted(filtered_files))

    # Determine output behavior
    should_print = print_output or (file is None)

    # Write output
    write_output(output, file, encoding, should_print)
