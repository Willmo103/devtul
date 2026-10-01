"""
List files command for devtul - lists repository files with pattern filtering and format exports.
"""

from pathlib import Path
from typing import List, Optional

import typer

from devtul.core.command import FileCommand
from devtul.core.constants import FileContentStatus
from devtul.core.models import FileFilterOptions, FilePath, ListingResult
from devtul.core.utils import write_to_file


class ListFilesCommand(FileCommand):
    """Command that lists repository or directory files with pattern filtering and format export."""

    name = "ls"
    help = "List repository files with format export and unix-like pattern filtering."

    @property
    def usage(self) -> str:
        return "dt ls [PATH] [OPTIONS]"

    @property
    def examples(self) -> list[str]:
        return [
            "dt ls ./my-repo",
            'dt ls ./my-repo --match "*.py"',
            'dt ls ./my-repo -e "tests/" -e "*test*"',
            "dt ls ./my-repo -e .\\tests\\test_migration_and_paths.py",
            "dt ls ./my-repo --json",
            "dt ls ./my-repo --yaml",
            "dt ls ./my-repo --csv",
            "dt ls --debug",
        ]

    def execute(
        self,
        path: Path = Path.cwd().resolve(),
        file: Optional[Path] = None,
        match: List[str] = [],
        exclude: List[str] = [],
        include_empty: bool = False,
        only_empty: bool = False,
        git: bool = True,
        json: bool = False,
        yaml: bool = False,
        csv: bool = False,
        override_ignore: bool = False,
        debug: bool = False,
    ) -> Optional[ListingResult]:
        if not path.exists():
            typer.echo(f"Error: Path {path} does not exist", err=True)
            raise typer.Exit(1)

        effective_git = False if override_ignore else git
        no_ignore = override_ignore
        effective_empty = True if (only_empty or include_empty) else False

        options = FileFilterOptions(
            path=path,
            match=match,
            exclude=exclude,
            git=effective_git,
            include_empty=effective_empty,
            no_ignore=no_ignore,
            debug=debug,
        )

        filtered_results, metrics = self.gather_and_filter_files(options)

        # If only_empty was requested, apply post-filter
        if only_empty:
            filtered_results = [
                res for res in filtered_results if res.content_status == FileContentStatus.EMPTY
            ]

        if not filtered_results:
            typer.echo("No files match the specified criteria", err=True)
            return None

        output_paths = sorted([res.relative_path.as_posix() for res in filtered_results])

        result = ListingResult(
            command_name=self.name,
            root_path=FilePath.from_path(path),
            files=filtered_results,
            metrics=metrics,
            relative_paths=output_paths,
        )

        # Render format
        fmt = "text"
        if json:
            fmt = "json"
        elif yaml:
            fmt = "yaml"
        elif csv:
            fmt = "csv"

        output = result.render(format=fmt)

        if file is None:
            typer.echo(output)
        else:
            write_to_file(output, file)

        return result


_ls_cmd = ListFilesCommand()


def ls(
    path: Path = typer.Argument(
        Path().cwd().resolve(),
        help="Path to the repository or directory",
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
    only_empty: bool = typer.Option(
        False, "--only-empty", help="Only include empty files"
    ),
    git: bool = typer.Option(
        True, "--git/--no-git", help="Look for git files or all files"
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
    debug: bool = typer.Option(
        False, "--debug", help="Print debug information for pattern matching"
    ),
):
    return _ls_cmd.execute(
        path=path,
        file=file,
        match=match,
        exclude=exclude,
        include_empty=include_empty,
        only_empty=only_empty,
        git=git,
        json=json,
        yaml=yaml,
        csv=csv,
        override_ignore=override_ignore,
        debug=debug,
    )


ls.__doc__ = _ls_cmd.get_formatted_help()


def entry():
    typer.run(ls)
