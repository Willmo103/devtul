from devtul.core.filters import find_all_dirs_containing_marker_file, find_all_dirs_containing_marker_folder, should_ignore_path
from pathlib import Path
from typing import List, Optional
import typer


def find_folder(
    root: Path = typer.Argument(
        Path().cwd().resolve(), help="Root path to start searching from"
    ),
    with_dir: Optional[str] = typer.Option(
        None, "--with-dir", help="Directory name pattern to look for"
    ),
    with_file: Optional[str] = typer.Option(
        None, "--with-file", help="Filename pattern to look for"
    ),
    filter: bool = typer.Option(True, "--filter/--all", help="Apply filtering"),
) -> Optional[List[Path]]:
    """
    Find directories containing a specific marker file or folder.
    """
    if with_dir:
        files = find_all_dirs_containing_marker_folder(root, with_dir)
        for f in files:
            if filter and should_ignore_path(f):
                continue
            else:
                typer.echo(f.resolve().as_posix())
    if with_file:
        files = find_all_dirs_containing_marker_file(root, with_file)
        for f in files:
            if filter and should_ignore_path(f):
                continue
            else:
                typer.echo(f.resolve().as_posix())

    return None
