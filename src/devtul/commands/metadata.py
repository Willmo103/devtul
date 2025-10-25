"""
Metadata command for devtul - displays git repository metadata.
"""

# import json
from pathlib import Path
from typing import Optional

import typer
import yaml

from devtul.core.utils import render_template
from ..core import format_git_metadata_table, get_git_metadata, write_to_file


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

    if (path / ".git").exists():
        # Get git metadata
        git_metadata = get_git_metadata(path)
    else:
        print("Not a git repository")
        return

    # Format output
    # if json_format:
    #     output = git_metadata.model_dump_json(indent=4)
    # else:
    #     output = format_git_metadata_table(git_metadata)

    render_template("git_yaml.yml.jinja", obj=git_metadata.model_dump())

    # if file is None:
    #     print(output)
    #     return
    # else:
    #     # Write output
    #     write_to_file(output, file)
