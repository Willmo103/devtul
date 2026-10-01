"""
Find command for devtul - searches for terms in repository files.
"""

import json
from pathlib import Path
from typing import List, Optional

import typer

from devtul.core.command import FileCommand
from devtul.core.file_utils import search_in_file
from devtul.core.models import FileFilterOptions, FilePath, FindResult
from devtul.core.utils import write_to_file


class FindCommand(FileCommand):
    """Command that searches for text patterns within repository files."""

    name = "find"
    help = "Search for a term within repository files."

    @property
    def usage(self) -> str:
        return "dt find TERM [OPTIONS]"

    @property
    def examples(self) -> list[str]:
        return [
            'dt find "function" ./my-repo',
            'dt find "TODO" --match "*.py"',
            'dt find "import" -e "tests/" -e "*test*"',
            'dt find "typer" -e .\\tests\\test_migration_and_paths.py',
            'dt find "typer" --json',
            'dt find "typer" --table',
            'dt find "typer" --debug',
        ]

    def execute(
        self,
        term: str,
        path: Path = Path.cwd().resolve(),
        file: Optional[Path] = None,
        match: List[str] = [],
        exclude: List[str] = [],
        json_format: bool = False,
        table_format: bool = False,
        git: bool = True,
        no_ignore: bool = False,
        debug: bool = False,
    ) -> Optional[FindResult]:
        if not path.exists():
            typer.echo(f"Error: Path {path} does not exist", err=True)
            raise typer.Exit(1)

        options = FileFilterOptions(
            path=path,
            match=match,
            exclude=exclude,
            git=git,
            include_empty=False,
            no_ignore=no_ignore,
            debug=debug,
        )

        filtered_results, metrics = self.gather_and_filter_files(options)
        if not filtered_results:
            typer.echo("No files match the specified criteria", err=True)
            return None

        all_matches = []
        for res in sorted(filtered_results, key=lambda x: x.relative_path.as_posix()):
            full_path = res.full_path
            matches = search_in_file(full_path, term)
            for m in matches:
                m.file_path = full_path.as_posix()
                m.relative_path = res.relative_path.as_posix()
                all_matches.append(m)

        if not all_matches:
            output = f"No matches found for term: {term}"
        else:
            if json_format:
                output = json.dumps(
                    {
                        "search_term": term,
                        "total_matches": len(all_matches),
                        "matches": [m.model_dump() for m in all_matches],
                    },
                    indent=2,
                )
            elif table_format:
                table_lines = [
                    "| File | Line | Content |",
                    "|------|------|---------|",
                ]
                for m in all_matches:
                    f_path = m.relative_path
                    line_num = m.line_number
                    content = m.content[:100] + ("..." if len(m.content) > 100 else "")
                    content = content.replace("|", "\\|")
                    table_lines.append(f"| {f_path} | {line_num} | {content} |")
                output = "\n".join(table_lines)
            else:
                lines = []
                for m in all_matches:
                    if not m.is_error():
                        lines.append(m.as_line())
                output = "\n".join(lines)

        if file is not None:
            write_to_file(output, file)
        else:
            typer.echo(output)

        return FindResult(
            command_name=self.name,
            root_path=FilePath.from_path(path),
            files=filtered_results,
            metrics=metrics,
            term=term,
            matches=all_matches,
        )


_find_cmd = FindCommand()


def find(
    term: str = typer.Argument(..., help="Search term to find in files"),
    path: Path = typer.Option(
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
    json_format: bool = typer.Option(
        False, "--json", help="Output as JSON instead of table"
    ),
    table_format: bool = typer.Option(False, "--table", help="Output as table format"),
    git: bool = typer.Option(
        True, "--git/--no-git", help="Look for git files or all files"
    ),
    no_ignore: bool = typer.Option(
        False, "--no-ignore", help="Do not apply default ignore patterns"
    ),
    debug: bool = typer.Option(
        False, "--debug", help="Print debug information for pattern matching"
    ),
):
    return _find_cmd.execute(
        term=term,
        path=path,
        file=file,
        match=match,
        exclude=exclude,
        json_format=json_format,
        table_format=table_format,
        git=git,
        no_ignore=no_ignore,
        debug=debug,
    )


find.__doc__ = _find_cmd.get_formatted_help()


def entry():
    typer.run(find)
