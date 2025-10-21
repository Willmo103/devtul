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
    write_to_file,
)


def git_meta(
    path: Path = typer.Argument(
        Path().cwd().resolve(),
        help="Path to the git repository",
        callback=lambda v: Path(v).resolve(),
    ),
    file: Optional[Path] = typer.Option(None, "-f", "--file", help="Output file path"),
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

    if git and not (path / ".git").exists():
        print("Not a git repository")
        return

    # Get git metadata
    git_metadata = get_git_metadata(path)

    # Format output
    if json_format:
        output = json.dumps(git_metadata, indent=2, default=str)
    else:
        output = format_git_metadata_table(git_metadata)

    if file is None:
        print(output)
        return
    else:
        # Write output
        write_to_file(output, file)
