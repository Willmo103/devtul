"""
Command 'dt rpr' / 'dt-rpr'.
Unified repository representation suite with multi-format generation (Markdown, Word .docx, Plain Text)
and 'rpr clone' remote repository inspector.
"""

from datetime import datetime
from pathlib import Path
import shutil
import tempfile
from typing import List, Optional, Tuple, Union

from git import Repo as GitRepo
from rich.console import Console
import typer
from typing_extensions import Annotated

from devtul.core.command import FileCommand
from devtul.core.docx_processor import DocxProcessor
from devtul.core.file_utils import build_tree_structure, is_git_repo
from devtul.core.models import (
    FileFilterOptions,
    FilePath,
    FileResult,
    RepoMarkdownHeader,
    ReprResult,
)
from devtul.core.utils import get_markdown_mapping, write_to_file
from devtul.git.utils import format_git_metadata_table, get_git_metadata

console = Console()


class RprCommand(FileCommand):
    """
    Command that generates multi-format repository representations (Markdown, Word .docx, Plain Text).
    """

    name = "rpr"
    help = "Generate multi-format repository representations (Markdown, Word .docx, Plain Text)."

    @property
    def usage(self) -> str:
        return "dt rpr [PATH] [OPTIONS]\n  dt rpr clone <REPO_URL> [OPTIONS]"

    @property
    def examples(self) -> list[str]:
        return [
            "dt rpr . -f repo.docx",
            "dt rpr . --format docx -f documentation.docx",
            "dt rpr ./src --match '*.py' -f repo.md",
            "dt rpr clone https://github.com/user/repo -f remote_repo.docx",
            "dt rpr clone https://github.com/user/repo --dest ./local_checkout",
        ]

    def build_markdown(
        self,
        path: Path,
        filtered_results: List[FileResult],
        total_scanned: int,
        file_meta: bool = True,
        git_mode: bool = True,
        fmt_parent: bool = True,
    ) -> str:
        """Constructs the comprehensive markdown representation of the repository."""
        filtered_files_paths = sorted([res.relative_path.as_posix() for res in filtered_results])
        git_metadata = get_git_metadata(path) if git_mode else None
        tree_structure = build_tree_structure(
            filtered_files_paths, parent=path.as_posix(), fmt_parent=fmt_parent
        )

        markdown_content = []

        # YAML frontmatter
        frontmatter = RepoMarkdownHeader(
            generated_at=datetime.now().isoformat(),
            repo_path=str(path.absolute()),
            file_count=total_scanned,
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

        return "\n".join(markdown_content)

    def execute(
        self,
        path: Path = Path.cwd().resolve(),
        file: Optional[Path] = None,
        format: str = "md",
        docx_flag: bool = False,
        md_flag: bool = False,
        match: List[str] = [],
        exclude: List[str] = [],
        include_empty: bool = False,
        file_meta: bool = True,
        git: bool = True,
        no_ignore: bool = False,
        debug: bool = False,
        fmt_parent: bool = True,
    ) -> Optional[ReprResult]:
        resolved_path = path.resolve()
        if not resolved_path.exists():
            console.print(f"[bold red]Error: Path '{resolved_path}' does not exist.[/bold red]")
            raise typer.Exit(1)

        has_git = is_git_repo(resolved_path)
        git_mode = git and has_git

        options = FileFilterOptions(
            path=resolved_path,
            match=match,
            exclude=exclude,
            git=git,
            include_empty=include_empty,
            no_ignore=no_ignore,
            debug=debug,
        )

        filtered_results, metrics = self.gather_and_filter_files(options)
        if not filtered_results:
            console.print("[yellow]No files match the specified criteria.[/yellow]")
            return None

        resolved_format = format.lower()
        if docx_flag:
            resolved_format = "docx"
        elif md_flag:
            resolved_format = "md"
        elif file is not None:
            ext = file.suffix.lower()
            if ext == ".docx":
                resolved_format = "docx"
            elif ext in [".txt", ".text"]:
                resolved_format = "text"
            elif ext in [".md", ".markdown"]:
                resolved_format = "md"

        markdown_text = self.build_markdown(
            path=resolved_path,
            filtered_results=filtered_results,
            total_scanned=metrics.total_scanned,
            file_meta=file_meta,
            git_mode=git_mode,
            fmt_parent=fmt_parent,
        )

        output_content: Union[str, bytes] = markdown_text

        if resolved_format == "docx":
            if file is None:
                default_name = f"{resolved_path.name or 'repo'}_repr.docx"
                file = Path(default_name).resolve()
            DocxProcessor.convert_markdown_to_docx(markdown_text, file)
            console.print(f"[bold green]Successfully generated Word representation: {file}[/bold green]")
        elif resolved_format == "text":
            output_content = markdown_text
            if file is not None:
                write_to_file(markdown_text, file)
                console.print(f"[bold green]Successfully wrote text representation to {file}[/bold green]")
            else:
                typer.echo(markdown_text)
        else:  # md
            output_content = markdown_text
            if file is not None:
                write_to_file(markdown_text, file)
                console.print(f"[bold green]Successfully wrote markdown representation to {file}[/bold green]")
            else:
                typer.echo(markdown_text)

        return ReprResult(
            root_path=FilePath.from_path(resolved_path),
            files=filtered_results,
            metrics=metrics,
            format=resolved_format,
            content=output_content,
            output_file=file,
        )


command_instance = RprCommand()


def rpr_command(
    target: Annotated[
        str,
        typer.Argument(
            help="Directory path to represent (default: current directory), or 'clone'.",
            show_default=False,
        ),
    ] = ".",
    url: Annotated[
        Optional[str],
        typer.Argument(
            help="Remote repository URL (required when target is 'clone').",
            show_default=False,
        ),
    ] = None,
    file: Annotated[
        Optional[Path],
        typer.Option(
            "-f",
            "--file",
            help="Path to save the generated representation file.",
        ),
    ] = None,
    format: Annotated[
        str,
        typer.Option(
            "-fmt",
            "--format",
            help="Output format: 'md' (Markdown), 'docx' (Word), or 'text'.",
        ),
    ] = "md",
    docx: Annotated[
        bool,
        typer.Option(
            "--docx",
            "-dx",
            help="Shortcut to generate Word document (.docx).",
        ),
    ] = False,
    md: Annotated[
        bool,
        typer.Option(
            "--md",
            help="Shortcut to generate Markdown file (.md).",
        ),
    ] = False,
    match: Annotated[
        List[str],
        typer.Option(
            "-m",
            "--match",
            help="Unix-style pattern to include files (can be specified multiple times).",
        ),
    ] = [],
    exclude: Annotated[
        List[str],
        typer.Option(
            "-e",
            "--exclude",
            help="Unix-style pattern to exclude files (can be specified multiple times).",
        ),
    ] = [],
    dest: Annotated[
        Optional[Path],
        typer.Option(
            "--dest",
            "-d",
            help="Destination folder for 'rpr clone' (if omitted, uses temporary folder).",
        ),
    ] = None,
    depth: Annotated[
        Optional[int],
        typer.Option(
            "--depth",
            help="Commit depth for 'rpr clone' shallow cloning.",
        ),
    ] = None,
    include_empty: Annotated[
        bool,
        typer.Option(
            "--empty/--no-empty",
            "-E",
            help="Include empty files in representation.",
        ),
    ] = False,
    file_meta: Annotated[
        bool,
        typer.Option(
            "--filemeta/--no-filemeta",
            "-fm",
            help="Include file metadata tables in output.",
        ),
    ] = True,
    git: Annotated[
        bool,
        typer.Option(
            "--git/--no-git",
            "-g",
            help="Filter files using git tracked index if in a git repository.",
        ),
    ] = True,
    no_ignore: Annotated[
        bool,
        typer.Option(
            "--no-ignore",
            "-ni",
            help="Do not apply default file ignore patterns.",
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help="Enable verbose path resolution and pattern matching debug output.",
        ),
    ] = False,
    fmt_parent: Annotated[
        bool,
        typer.Option(
            "--fmt-parent/--no-fmt-parent",
            "--parent/--fmt-root",
            help="Display only the parent folder name as tree root (use --fmt-root or --no-fmt-parent for full path).",
        ),
    ] = True,
) -> Optional[ReprResult]:
    """Generate repository representation (Markdown, Word .docx, Plain Text), or clone and represent a remote repo."""
    # Check if this is a 'clone' invocation
    if target.lower() == "clone":
        if not url:
            console.print("[bold red]Error: 'rpr clone' requires a repository URL as the second argument.[/bold red]")
            console.print("Example: [cyan]dt rpr clone https://github.com/user/repo -f repo.docx[/cyan]")
            raise typer.Exit(code=1)

        is_temp = dest is None
        temp_dir_obj = None

        if is_temp:
            temp_dir_obj = tempfile.TemporaryDirectory(prefix="dt_clone_")
            target_clone_path = Path(temp_dir_obj.name)
        else:
            target_clone_path = dest.resolve()
            target_clone_path.mkdir(parents=True, exist_ok=True)

        console.print(f"[cyan]Cloning '{url}' into '{target_clone_path}'...[/cyan]")
        try:
            clone_kwargs = {}
            if depth:
                clone_kwargs["depth"] = depth
            GitRepo.clone_from(url, str(target_clone_path), **clone_kwargs)
        except Exception as e:
            console.print(f"[bold red]Failed to clone repository '{url}': {e}[/bold red]")
            if temp_dir_obj:
                try:
                    temp_dir_obj.cleanup()
                except Exception:
                    pass
            raise typer.Exit(code=1)

        try:
            return command_instance.execute(
                path=target_clone_path,
                file=file,
                format=format,
                docx_flag=docx,
                md_flag=md,
                match=match,
                exclude=exclude,
                include_empty=include_empty,
                file_meta=file_meta,
                git=True,
                no_ignore=no_ignore,
                debug=debug,
                fmt_parent=fmt_parent,
            )
        finally:
            if is_temp and temp_dir_obj:
                console.print("[dim]Cleaning up temporary clone directory...[/dim]")
                try:
                    temp_dir_obj.cleanup()
                except Exception as e:
                    if debug:
                        console.print(f"[dim]Note: could not immediately clean temp dir: {e}[/dim]")

    # Standard representation invocation
    target_path = Path(target).resolve()
    return command_instance.execute(
        path=target_path,
        file=file,
        format=format,
        docx_flag=docx,
        md_flag=md,
        match=match,
        exclude=exclude,
        include_empty=include_empty,
        file_meta=file_meta,
        git=git,
        no_ignore=no_ignore,
        debug=debug,
        fmt_parent=fmt_parent,
    )


def entry() -> None:
    """Standalone console entry point for dt-rpr."""
    typer.run(rpr_command)
