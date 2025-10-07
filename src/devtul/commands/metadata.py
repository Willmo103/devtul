"""
Metadata command for devtul - displays git repository metadata.
"""

import json
from pathlib import Path
from typing import Optional

import typer

from ..core import (
    format_git_metadata_table,
    get_git_metadata,
    write_output,
)


def git_meta(
    path: Path = typer.Argument(..., help="Path to the git repository"),
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
    file: Optional[Path] = typer.Option(
        None, "-f", "--file", help="Output file path"
    ),
    json_format: bool = typer.Option(
        False, "--json", help="Output as JSON instead of markdown table"
    ),
):
    """
    Display git repository metadata.

    Shows git repository information including branches, commits, remotes, and status.
    Can output as markdown table or JSON format.

    Examples:
        meta ./my-repo
        meta ./my-repo --json --print
        meta ./my-repo -f metadata.json --json
    """
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    if not (path / ".git").exists():
        output = "Not a git repository"
        should_print = print_output or (file is None)
        write_output(output, file, encoding, should_print)
        return

    # Get git metadata
    git_metadata = get_git_metadata(path)

    # Format output
    if json_format:
        output = json.dumps(git_metadata, indent=2, default=str)
    else:
        output = format_git_metadata_table(git_metadata)

    # Determine output behavior
    should_print = print_output or (file is None)

    # Write output
    write_output(output, file, encoding, should_print)
