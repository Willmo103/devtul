from pathlib import Path
from typing import Optional

import typer
from devtul.core.file_utils import copy_files


def copy(
        path: str = typer.Argument(
            Path().cwd().resolve(), help="Path to the git repository", callback=lambda v: Path(v).resolve()
        ),
        dest: Path = typer.Option(
            ..., "-d", "--dest", help="Destination path to copy files to"
        ),
        git: bool = typer.Option(
            True, "--git/--no-git", help="look for git files or all files"
        ),
        zip: bool = typer.Option(
            False, "--zip", help="Create a zip archive of the copied files"
        ),
):
    """
    Copy files from the specified path to a destination ignoreing all default ignore patterns.
    Examples:
        copy ./my-repo --dest ./backup
        copy ./my-repo --dest ./backup --zip
    """
    if not dest.exists():
        dest.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    source_path = Path(path).resolve()
    dest = dest.resolve()
    copy_files(source_path, dest, git=git, zip=zip)
