"""
List files command for devtul - lists git tracked files.
"""

from pathlib import Path
from typing import List, Optional

import typer

from devtul.core.file_utils import get_all_files
from devtul.core import (
    apply_filters,
    get_git_files,
    write_to_file,
)


def ls(
    path: Path = typer.Argument(
        Path().cwd().resolve(), help="Path to the git repository"
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
    only_empty: bool = typer.Option(
        False, "--only-empty", help="Only include empty files"
    ),
    git: bool = typer.Option(
        True, "--git/--no-git", help="look for git files or all files"
    ),
    json: bool = typer.Option(
        False, "--json", help="Output as JSON instead of plain text"
    ),
    yaml: bool = typer.Option(
        False, "--yaml", help="Output as YAML instead of plain text"
    ),
    csv: bool = typer.Option(
        False, "--csv", help="Output as CSV instead of plain text"
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

    if git:
        if not (path / ".git").exists():
            all_files = get_all_files(
                path, include_empty=include_empty, only_empty=only_empty
            )
        else:
            # Get git files
            all_files = get_git_files(
                path, include_empty=include_empty, only_empty=only_empty
            )
    if not git:
        # Get all files
        all_files = get_all_files(
            path, include_empty=include_empty, only_empty=only_empty
        )

    # Apply match/exclude filters
    filtered_files = apply_filters(all_files, match, exclude)

    if not filtered_files:
        typer.echo("No files match the specified criteria", err=True)
        raise typer.Exit(1)

    # Create output
    if json:
        output = typer.style("[", fg=typer.colors.GREEN)
        for i, f in enumerate(sorted(filtered_files)):
            output += typer.style(f'"{f}"', fg=typer.colors.YELLOW)
            if i < len(filtered_files) - 1:
                output += typer.style(",", fg=typer.colors.GREEN)
        output += typer.style("]", fg=typer.colors.GREEN)
    elif yaml:
        output = f"path: {path.as_posix()}\n  files:\n"
        for f in sorted(filtered_files):
            output += f"    - {f}\n"
    elif csv:
        output = f"files - {path.as_posix()}\n"
        for f in sorted(filtered_files):
            output += f"'{f.replace("\\", "/")}'\n"
    else:
        output = "\n".join(sorted(filtered_files))

    if file is None:
        # Print to stdout
        typer.echo(output)
    else:
        # Write output
        write_to_file(output, file)
