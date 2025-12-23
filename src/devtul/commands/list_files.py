"""
List files command for devtul - lists git tracked files.
"""

import sys
from pathlib import Path
from typing import List, Optional

import typer

from devtul.core.file_utils import (
    gather_all_paths,
    try_gather_all_git_tracked_paths,
    filter_gathered_paths_by_path_parts,
    filter_gathered_paths_by_patterns,
    filter_paths_for_empty_files,
)
from devtul.core.models import FileResult
from devtul.core.utils import write_to_file


def ls(
    path: Path = typer.Argument(
        Path().cwd().resolve(), help="Path to the git repository"
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
    only_empty: bool = typer.Option(
        False, "--only-empty", help="Only include empty files"
    ),
    git: bool = typer.Option(
        True, "--git/--no-git", help="look for git files or all files"
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
    override_ignore: bool = typer.Option(
        False,
        "-o",
        "--override-ignore",
        help="Override default ignore patterns and include all files",
    ),
):
    """
    List git tracked files with optional filtering.

    Behaves like 'git ls-files' but with additional filtering capabilities.
    By default excludes empty files and supports pattern matching.

    Examples:
        ls ./my-repo
        ls ./my-repo --match "*.py" --print
        ls ./my-repo --sub-dir src -f files_list.txt
    """
    if override_ignore:
        git = False

    if not path.exists():
        typer.echo(f"Error: Path {path} does not exist", err=True)
        raise typer.Exit(1)

    # 1. Gather Paths
    if git:
        paths = try_gather_all_git_tracked_paths(path)
    else:
        paths = gather_all_paths(path)

    # 2. Filter Paths (ignore parts/patterns)
    # If override_ignore is True, we skip default ignores?
    # The original code logic for override_ignore was:
    # if override_ignore: return rglob("*")
    # Here we can just skip the filtering helpers if override_ignore is set.

    if not override_ignore:
         # Note: file_utils constants imports might be needed if we want to use defaults from there
         # But the functions in file_utils seem to use internal imports or args.
         # Let's import the defaults to pass them if needed, or rely on functions.
         # Looking at file_utils, filter_gathered_paths_dy_default_ignores uses the constants.
         from devtul.core.file_utils import filter_gathered_paths_dy_default_ignores
         paths = filter_gathered_paths_dy_default_ignores(paths)

    # Apply user supplied exclude/match on paths directly?
    # The user said "filtering should happed after the list of FileResult objects are retrund".
    # So let's convert to FileResults first as requested.

    # However, filtering paths first is much more efficient.
    # But sticking to user instructions: "after the list of FileResult objects".

    # 3. Convert to FileResult objects
    file_results = []
    # We only want files, not directories, for 'ls' typically?
    # Original ls command: `if path.is_file()...`
    # gather_all_paths returns dirs too.

    for p in paths:
        if p.is_file():
             file_results.append(FileResult(p, path))

    # 4. Filter FileResults
    filtered_results = []
    for res in file_results:
        # Check match patterns
        if match:
            # Check if ANY match pattern matches
            import fnmatch
            if not any(fnmatch.fnmatch(res.relative_path.as_posix(), m) for m in match):
                continue

        # Check exclude patterns
        if exclude:
            import fnmatch
            if any(fnmatch.fnmatch(res.relative_path.as_posix(), e) for e in exclude):
                continue

        # Check empty
        # FileResult has content_status
        from devtul.core.constants import FileContentStatus
        if only_empty:
            if res.content_status != FileContentStatus.EMPTY:
                continue
        elif not include_empty:
             if res.content_status == FileContentStatus.EMPTY:
                 continue

        filtered_results.append(res)

    if not filtered_results:
        typer.echo("No files match the specified criteria", err=True)
        # raise typer.Exit(1) # Don't exit error, just empty? Original raised exit 1.
        return

    # 5. Output
    # Need to extract paths for output
    output_paths = [res.relative_path.as_posix() for res in filtered_results]
    output_paths.sort()

    if json:
        import json as json_lib
        output = json_lib.dumps(output_paths)
    elif yaml:
        import yaml as yaml_lib
        output = yaml_lib.dump({"path": path.as_posix(), "files": output_paths})
    elif csv:
        output = f"files - {path.as_posix()}\n"
        for f in output_paths:
            output += f"'{f}'\n"
    else:
        output = "\n".join(output_paths)

    if file is None:
        typer.echo(output)
    else:
        write_to_file(output, file)

def entry():
    typer.run(ls)
