import os
from pathlib import Path
from typing import List, Optional

import typer

empty = typer.Typer(
    name="empty",
    help="Locate empty files and folders in the specified path.",
    invoke_without_command=True,
    no_args_is_help=False,
)


@empty.callback(invoke_without_command=True)
def empty_callback(
    ctx: typer.Context,
    files: bool = typer.Option(
        False, "--files", help="Locate empty files and return full paths"
    ),
    folders: bool = typer.Option(
        False, "--folders", "--dirs", help="Locate empty folders and return full paths"
    ),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to search for empty files or folders"
    ),
    git: Optional[bool] = typer.Option(
        None, "--git/--no-git", help="Look for git-tracked files or all files"
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
    """Callback allowing 'dt empty --folders' or 'dt empty --files' directly."""
    if ctx.invoked_subcommand is not None:
        return

    if not files and not folders:
        typer.echo(ctx.get_help())
        raise typer.Exit()

    target_path = (path or Path.cwd()).resolve()

    if files:
        locate_empty_files(
            path=target_path,
            git=git,
            json=json,
            yaml=yaml,
            csv=csv,
        )
    if folders:
        find_empty_folders(
            path=target_path,
            json=json,
            yaml=yaml,
            csv=csv,
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
    ),
):
    """
    Locate empty files in the specified path and return their full paths.
    Examples:
        dt empty files ./my-repo
        dt empty --files --path ./my-repo
    """
    path = path.resolve()
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    # 1. Gather Paths
    use_git = False
    if git is True:
        use_git = True
    elif git is None:
        if (path / ".git").exists():
            use_git = True

    if use_git:
        from devtul.core.file_utils import try_gather_all_git_tracked_paths

        paths = try_gather_all_git_tracked_paths(path)
    else:
        from devtul.core.file_utils import gather_all_paths

        paths = gather_all_paths(path)

    # 2. Filter via FileResult pipeline - Only Empty
    from devtul.core.constants import FileContentStatus
    from devtul.core.models import FileResult

    empty_items: List[str] = []

    for p in paths:
        if p.is_file():
            if p.stat().st_size == 0:
                res = FileResult(p, path)
                if res.content_status == FileContentStatus.EMPTY:
                    # Return full path formatted with forward slashes
                    empty_items.append(res.full_path.as_posix())

    if not empty_items:
        print("No empty items found.")
        return

    empty_items = sorted(empty_items)

    if json:
        output = typer.style("[", fg=typer.colors.GREEN)
        for i, f in enumerate(empty_items):
            output += typer.style(f'"{f}"', fg=typer.colors.YELLOW)
            if i < len(empty_items) - 1:
                output += typer.style(",", fg=typer.colors.GREEN)
        output += typer.style("]", fg=typer.colors.GREEN)
    elif yaml:
        output = f"path: {path.as_posix()}\n  empty_files:\n"
        for f in empty_items:
            output += f"    - {f}\n"
    elif csv:
        output = f"empty_files - {path.as_posix()}\n"
        for f in empty_items:
            f = f.replace("\\", "/")
            output += f"'{f}'\n"
    else:
        output = "\n".join(empty_items)

    print(output)


@empty.command(name="dirs", help="Locate empty folders in the specified path.")
def find_empty_folders(
    path: Path = typer.Argument(
        Path().cwd().resolve(), help="Path to search for empty folders"
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
    Locate empty folders in the specified path and return their full paths.
    Examples:
        dt empty dirs ./my-repo
        dt empty --folders --path ./my-repo
    """
    path = path.resolve()
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    empty_folders: List[str] = []

    for dirpath, dirnames, filenames in os.walk(path):
        if not dirnames and not filenames:
            # Return full path formatted with forward slashes
            empty_folders.append(Path(dirpath).resolve().as_posix())

    if not empty_folders:
        print("No empty folders found.")
        return

    empty_folders = sorted(empty_folders)

    if json:
        output = typer.style("[", fg=typer.colors.GREEN)
        for i, f in enumerate(empty_folders):
            output += typer.style(f'"{f}"', fg=typer.colors.YELLOW)
            if i < len(empty_folders) - 1:
                output += typer.style(",", fg=typer.colors.GREEN)
        output += typer.style("]", fg=typer.colors.GREEN)
    elif yaml:
        output = f"path: {path.as_posix()}\n  empty_folders:\n"
        for f in empty_folders:
            output += f"    - {f}\n"
    elif csv:
        output = f"empty_folders - {path.as_posix()}\n"
        for f in empty_folders:
            f = f.replace("\\", "/")
            output += f"'{f}'\n"
    else:
        output = "\n".join(empty_folders)

    print(output)


@empty.command(
    name="folders", help="Locate empty folders in the specified path (alias for dirs)."
)
def find_empty_folders_alias(
    path: Path = typer.Argument(
        Path().cwd().resolve(), help="Path to search for empty folders"
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
    """Alias for 'dirs'."""
    find_empty_folders(path=path, json=json, yaml=yaml, csv=csv)


def entry():
    empty()
