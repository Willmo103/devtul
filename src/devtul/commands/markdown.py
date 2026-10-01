"""
Markdown command for devtul - generates comprehensive markdown documentation.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer

from devtul.core.command import FileCommand
from devtul.core.file_utils import build_tree_structure, is_git_repo
from devtul.core.models import (
    FileFilterOptions,
    FilePath,
    MarkdownResult,
    RepoMarkdownHeader,
)
from devtul.core.utils import get_markdown_mapping, write_to_file
from devtul.git.utils import format_git_metadata_table, get_git_metadata


class MarkdownCommand(FileCommand):
    """Command that creates a unified markdown document representation of repository files."""

    name = "md"
    help = "Generate comprehensive markdown documentation from repository files."

    @property
    def usage(self) -> str:
        return "dt md [PATH] [OPTIONS]"

    @property
    def examples(self) -> list[str]:
        return [
            "dt md ./my-repo",
            'dt md ./my-repo --match "*.py" -f repo_docs.md',
            'dt md ./my-repo --exclude "tests/" --exclude "*.png"',
            "dt md ./my-repo -e .\\tests\\test_migration_and_paths.py",
            "dt md --no-git --filemeta",
            "dt md --debug",
        ]

    def execute(
        self,
        path: Path = Path.cwd().resolve(),
        file: Optional[Path] = None,
        match: List[str] = [],
        exclude: List[str] = [],
        include_empty: bool = False,
        file_meta: bool = True,
        git: bool = True,
        no_ignore: bool = False,
        debug: bool = False,
    ) -> Optional[MarkdownResult]:
        if not path.exists():
            typer.echo(f"Error: Path {path} does not exist", err=True)
            raise typer.Exit(1)

        has_git = is_git_repo(path)
        git_mode = git and has_git

        options = FileFilterOptions(
            path=path,
            match=match,
            exclude=exclude,
            git=git,
            include_empty=include_empty,
            no_ignore=no_ignore,
            debug=debug,
        )

        filtered_results, metrics = self.gather_and_filter_files(options)
        if not filtered_results:
            typer.echo("No files match the specified criteria", err=True)
            return None

        filtered_files_paths = sorted([res.relative_path.as_posix() for res in filtered_results])
        git_metadata = get_git_metadata(path) if git_mode else None
        tree_structure = build_tree_structure(filtered_files_paths, parent=path.as_posix())

        markdown_content = []

        # YAML frontmatter
        frontmatter = RepoMarkdownHeader(
            generated_at=datetime.now().isoformat(),
            repo_path=str(path.absolute()),
            file_count=metrics.total_scanned,
            files_included=len(filtered_results),
        )
        markdown_content.append(frontmatter.frontmatter())

        if git_mode and git_metadata:
            repo_name = path.name.upper()
            markdown_content.append(f"# {repo_name}")
            markdown_content.append("")
            markdown_content.append("---")
            markdown_content.append("")
            markdown_content.append("## Git Metadata")
            markdown_content.append("")
            markdown_content.append(format_git_metadata_table(git_metadata))
            markdown_content.append("")
            markdown_content.append("---")
            markdown_content.append("")

        # Structure section
        markdown_content.append("## Structure")
        markdown_content.append("")
        markdown_content.append("```")
        markdown_content.append(tree_structure)
        markdown_content.append("```")
        markdown_content.append("")
        markdown_content.append("---")
        markdown_content.append("")
        markdown_content.append("## Files")
        markdown_content.append("")

        # File contents
        for res in sorted(filtered_results, key=lambda x: x.relative_path.as_posix()):
            try:
                full_path = res.full_path
                display_path = res.relative_path.as_posix()

                markdown_content.append(f"### {Path(display_path).name}")
                markdown_content.append("")

                if file_meta:
                    file_size = res.size
                    last_modified = res.modified_at.isoformat() if res.modified_at else "Unknown"
                    created_at = res.created_at.isoformat() if res.created_at else "Unknown"

                    max_key_length = len("Relative Path")
                    max_value_length = max(
                        len(display_path), len(str(last_modified)), len(str(file_size)) + 7
                    )
                    file_table = [
                        f"| {'Property'.ljust(max_key_length)} | {'Value'.ljust(max_value_length)} |",
                        "|"
                        + "-" * (max_key_length + 2)
                        + "|"
                        + "-" * (max_value_length + 2)
                        + "|",
                        f"| {'Relative Path'.ljust(max_key_length)} | {display_path.ljust(max_value_length)} |",
                        f"| {'Created At'.ljust(max_key_length)} | {str(created_at).ljust(max_value_length)} |",
                        f"| {'Last Modified'.ljust(max_key_length)} | {str(last_modified).ljust(max_value_length)} |",
                        f"| {'Size'.ljust(max_key_length)} | {(str(file_size) + ' bytes').ljust(max_value_length)} |",
                    ]

                    markdown_content.extend(file_table)
                    markdown_content.append("")
                else:
                    markdown_content.append(f"**Path:** `{display_path}`")
                    markdown_content.append("")

                markdown_content.append("**Content**:")
                markdown_content.append("")
                markdown_content.append("```" + get_markdown_mapping(full_path))
            except Exception as e:
                markdown_content.append(f"Error processing metadata for {full_path}: {e}")
                markdown_content.append("```")
                markdown_content.append("")
                continue

            try:
                with open(full_path, "r", encoding="utf8", errors="replace") as f:
                    content = f.read()
                    markdown_content.append(content)
            except Exception as e:
                markdown_content.append(f"Error reading file content: {e}")

            markdown_content.append("```")
            markdown_content.append("")
            markdown_content.append("---")
            markdown_content.append("")

        final_content = "\n".join(markdown_content)

        if file is not None:
            write_to_file(final_content, file)
        else:
            print(final_content)

        return MarkdownResult(
            command_name=self.name,
            root_path=FilePath.from_path(path),
            files=filtered_results,
            metrics=metrics,
            header=frontmatter,
            markdown_text=final_content,
        )


_markdown_cmd = MarkdownCommand()


def markdown(
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
    file_meta: bool = typer.Option(
        True, "--filemeta/--no-filemeta", help="Include file metadata tables"
    ),
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
    return _markdown_cmd.execute(
        path=path,
        file=file,
        match=match,
        exclude=exclude,
        include_empty=include_empty,
        file_meta=file_meta,
        git=git,
        no_ignore=no_ignore,
        debug=debug,
    )


markdown.__doc__ = _markdown_cmd.get_formatted_help()


def entry():
    typer.run(markdown)
