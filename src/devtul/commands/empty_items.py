import os
from pathlib import Path

import typer
from git import Optional

from devtul.core.file_utils import gather_all_paths, try_gather_all_git_tracked_paths

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
    ),
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

    # 1. Gather Paths
    # Logic for git default? Original code: `if git and (path / ".git").exists()...`
    # Here git is Optional[bool].
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
    from devtul.core.models import FileResult
    from devtul.core.constants import FileContentStatus

    empty_items = []

    # We can use filter_paths_for_empty_files from file_utils if we want, or manually check
    # But since we are mandated to use FileResult...

    # Wait, creating FileResult for ALL files just to check size might be slow if we have thousands.
    # But that's the requested pattern.
    # Actually, file_utils has `filter_paths_for_empty_files(paths) -> (non_empty, empty)`.
    # I should use that for efficiency and then wrap results?
    # Or just use FileResult is fine.

    for p in paths:
        if p.is_file():
             # Optimization: check stat size before full FileResult?
             if p.stat().st_size == 0:
                 # It's empty
                 # We need string path for output
                 # get_git_files returned relative strings. FileResult has relative_path.
                 # Let's use FileResult for consistency.
                 res = FileResult(p, path)
                 if res.content_status == FileContentStatus.EMPTY:
                     empty_items.append(res.relative_path.as_posix())

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
            f = f.replace("\\", "/")
            output += f"'{f}'\n"
    else:
        output = "\n".join(sorted(empty_items))

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

def entry():
    empty()
