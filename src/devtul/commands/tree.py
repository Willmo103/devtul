"""
Tree command for devtul - generates tree structures from git repositories.
"""

from pathlib import Path
from typing import List, Optional

import typer

from devtul.core.file_utils import (build_tree_structure, gather_all_paths,
                                    try_gather_all_git_tracked_paths)
from devtul.core.models import FileResult
from devtul.core.utils import write_to_file


def tree(
    path: Path = typer.Argument(
        Path().cwd().resolve(),
        help="Path to the git repository",
        callback=lambda v: Path(v).resolve(),
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
    git: bool = typer.Option(
        True, "--git/--no-git", help="Look for git tracked files or all files"
    ),
):
    """
    Generate a tree structure from git tracked files.

    Creates a visual tree representation of all files tracked by git in the specified repository.
    Uses the same tree characters as standard tree commands (├── └── │).

    Examples:
        tree ./my-repo
        tree ./my-repo --match "*.py" --match "*.md" --print
        tree ./my-repo --sub-dir src -f tree_output.txt
    """
    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    # 1. Gather Paths
    if git:
        paths = try_gather_all_git_tracked_paths(path)
    else:
        paths = gather_all_paths(path)

    # 2. Filter via FileResult pipeline
    if not git: # Should check override ignore logic similar to ls? The command doesn't have override_ignore arg here but gather_paths does default ignores?
        from devtul.core.file_utils import filter_gathered_paths_by_default_ignores

        paths = filter_gathered_paths_by_default_ignores(paths)

    file_results = []
    for p in paths:
        if p.is_file():
            file_results.append(FileResult(p, path))

    filtered_files = []
    # Reuse filtering logic (this should ideally be in a shared function now, but keeping inline per command for now)
    for res in file_results:
        if match:
            import fnmatch
            if not any(fnmatch.fnmatch(res.relative_path.as_posix(), m) for m in match):
                continue
        if exclude:
            import fnmatch
            if any(fnmatch.fnmatch(res.relative_path.as_posix(), e) for e in exclude):
                continue

        # Check empty
        from devtul.core.constants import FileContentStatus
        if not include_empty:
            if res.content_status == FileContentStatus.EMPTY:
                continue

        filtered_files.append(res.relative_path.as_posix()) # tree needs relative strings

    if not filtered_files:
        typer.echo("No files match the specified criteria", err=True)
        # raise typer.Exit(1)
        return

    # Build tree structure using the final filtered list
    # The helper expects paths relative to parent or just a list of paths?
    # build_tree_structure takes List[str].
    tree_output = build_tree_structure(filtered_files, parent=path.as_posix())

    # Determine output behavior
    if file is None:
        print(tree_output)
        return
    output_file = file
    if file is not None and file == Path():
        output_file = Path.cwd() / "file_tree.md"

    # Write output
    write_to_file(tree_output, output_file)

def entry():
    typer.run(tree)
