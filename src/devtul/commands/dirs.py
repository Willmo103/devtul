from pathlib import Path
from typing import List, Optional

import typer

from devtul.core.file_utils import (find_all_dirs_containing_file,
                                    find_all_dirs_containing_marker_folder)


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
    recurse: Optional[bool] = typer.Option(
        None, "-r/--recurse", help="Recurse into subdirectories"
    ),
) -> Optional[List[Path]]:
    """
    Find directories containing a specific marker file or folder.
    """
    found = []
    if with_dir:
        files = find_all_dirs_containing_marker_folder(root, with_dir, recurse=recurse)
        for f in files:
            found.append(f)
    if with_file:
        files = find_all_dirs_containing_file(root, with_file, recurse=recurse)
        for f in files:
            found.append(f)
    for f in found:
        typer.echo(f.as_posix())

def entry():
    typer.run(find_folder)
