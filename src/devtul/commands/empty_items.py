import os
from pathlib import Path

from git import Optional
from devtul.core.file_utils import get_all_files
from devtul.core.git_utils import get_git_files
import typer

empty = typer.Typer(
    name="empty",
    help="Locate empty files and folders in the specified path.",
)


@empty.command(name="files", help="Locate empty files in the specified path.")
def locate_empty_files(
        path: Path = typer.Argument(
            Path().cwd().resolve(), help="Path to search for empty files"
        ),
        git: Optional[bool] = typer.Option(
            None, "--git/--no-git", help="look for git files or all files"
        ),
        json: bool = typer.Option(
            False, "--json", help="Output as JSON instead of plain text"
        ),
        yaml: bool = typer.Option(
            False, "--yaml", help="Output as YAML instead of plain text"
        ),
        csv: bool = typer.Option(
            False, "--csv", help="Output as CSV instead of plain text"
        )
):
    """
    Locate empty files in the specified path.
    Examples:
        empty-items ./my-repo
        empty-items ./my-repo -f empty_files.txt
    """
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    if git and (path / ".git").exists():
        empty_items = get_git_files(
            path,
            only_empty=True
        )
    else:
        empty_items = get_all_files(
            path,
            only_empty=True,
        )
    if not empty_items:
        print("No empty items found.")
        return

    if json:
        output = typer.style("[", fg=typer.colors.GREEN)
        for i, f in enumerate(sorted(empty_items)):
            output += typer.style(f'"{f}"', fg=typer.colors.YELLOW)
            if i < len(empty_items) - 1:
                output += typer.style(",", fg=typer.colors.GREEN)
        output += typer.style("]", fg=typer.colors.GREEN)
    elif yaml:
        output = f"path: {path.as_posix()}\n  empty_files:\n"
        for f in sorted(empty_items):
            output += f"    - {f}\n"
    elif csv:
        output = f"empty_files - {path.as_posix()}\n"
        for f in sorted(empty_items):
            output += f"'{f.replace('\\', '/')}'\n"
    else:
        output = "\n".join(sorted(empty_items))

    print(output)


@empty.command(name="dirs", help="Locate empty folders in the specified path.")
def find_empty_folders(
        path: Path = typer.Argument(
            Path().cwd().resolve(), help="Path to search for empty folders"
        )
):
    """
    Locate empty folders in the specified path.
    Examples:
        empty-items ./my-repo
        empty-items ./my-repo -f empty_folders.txt
    """
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    empty_folders = []

    for dirpath, dirnames, filenames in os.walk(path):
        if not dirnames and not filenames:
            empty_folders.append(Path(dirpath).relative_to(path).as_posix())

    if not empty_folders:
        print("No empty folders found.")
        return

    output = "\n".join(sorted(empty_folders))

    print(output)
