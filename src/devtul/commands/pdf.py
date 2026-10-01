"""
Command 'dt ppdf' / 'dt print-pdf'.
Terminal PDF text inspector powered by pdfplumber and StringCommand stream filtering.
"""

from pathlib import Path
import sys
from typing import List, Optional

import pdfplumber
from rich.console import Console
import typer
from typing_extensions import Annotated

from devtul.core.command import StringCommand
from devtul.core.models import StringCommandResult, StringFilterOptions

console = Console()


def parse_page_range(spec: Optional[str], total_pages: int) -> List[int]:
    """
    Parses a page range string (e.g. '1-3', '2,4', '5') into 0-indexed page numbers.
    """
    if not spec:
        return list(range(total_pages))

    pages: List[int] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            bounds = part.split("-", 1)
            try:
                start = max(1, int(bounds[0]))
                end = min(total_pages, int(bounds[1]))
                pages.extend(range(start - 1, end))
            except ValueError:
                continue
        else:
            try:
                p = int(part)
                if 1 <= p <= total_pages:
                    pages.append(p - 1)
            except ValueError:
                continue
    return sorted(list(set(pages)))


class PrintPdfCommand(StringCommand):
    """
    Extracts text from PDF documents and applies line filtering.
    """

    name: str = "ppdf"
    help: str = "Extract and display text from PDF files with optional line filtering."

    @property
    def usage(self) -> str:
        return "dt ppdf <PATH> [OPTIONS]"

    @property
    def examples(self) -> list[str]:
        return [
            "dt ppdf document.pdf",
            "dt ppdf report.pdf --pages 1-3 --head 20",
            "dt ppdf invoice.pdf --grep 'Total' --numbered",
            "dt ppdf paper.pdf --lines-with 'conclusion'",
            "dt ppdf document.pdf --sed 's/foo/bar/g'",
        ]

    def execute(
        self,
        path: Path,
        pages: Optional[str] = None,
        head: Optional[int] = None,
        tail: Optional[int] = None,
        grep: Optional[str] = None,
        sed: Optional[str] = None,
        numbered: bool = False,
        lines_with: Optional[str] = None,
    ) -> StringCommandResult:
        resolved = path.resolve()
        if not resolved.exists():
            console.print(f"[bold red]Error: PDF file not found at '{resolved}'.[/bold red]")
            raise typer.Exit(code=1)

        raw_lines: List[str] = []
        try:
            with pdfplumber.open(resolved) as pdf:
                total_pages = len(pdf.pages)
                target_pages = parse_page_range(pages, total_pages)
                for page_idx in target_pages:
                    page = pdf.pages[page_idx]
                    page_text = page.extract_text()
                    if page_text:
                        raw_lines.extend(page_text.splitlines())
        except Exception as e:
            console.print(f"[bold red]Error reading PDF file '{resolved}': {e}[/bold red]")
            raise typer.Exit(code=1)

        options = StringFilterOptions(
            head=head,
            tail=tail,
            grep=grep,
            sed=sed,
            numbered=numbered,
            lines_with=lines_with,
        )

        filtered_lines = self.process_lines(raw_lines, options)
        self.render_console(filtered_lines, options, console=console)

        return StringCommandResult(
            command_name="ppdf",
            lines=filtered_lines,
            total_lines=len(filtered_lines),
        )


command_instance = PrintPdfCommand()


def print_pdf_command(
    path: Annotated[Path, typer.Argument(help="Path to the PDF file to inspect.")],
    pages: Annotated[
        Optional[str],
        typer.Option(
            "--pages",
            "-p",
            help="Page numbers or ranges to inspect (e.g. '1-3', '2,5').",
        ),
    ] = None,
    head: Annotated[
        Optional[int],
        typer.Option("--head", "-H", help="Display only the first N lines."),
    ] = None,
    tail: Annotated[
        Optional[int],
        typer.Option("--tail", "-T", help="Display only the last N lines."),
    ] = None,
    grep: Annotated[
        Optional[str],
        typer.Option(
            "--grep",
            "-g",
            help="Regex or substring pattern to filter matching lines.",
        ),
    ] = None,
    sed: Annotated[
        Optional[str],
        typer.Option(
            "--sed",
            "-s",
            help="Sed substitution pattern (e.g. 's/find/replace/g').",
        ),
    ] = None,
    numbered: Annotated[
        bool,
        typer.Option(
            "--numbered",
            "-n",
            help="Prefix output with 1-indexed line numbers.",
        ),
    ] = False,
    lines_with: Annotated[
        Optional[str],
        typer.Option(
            "--lines-with",
            "-l",
            help="Filter lines containing term and highlight matches in Rich terminal.",
        ),
    ] = None,
) -> None:
    """Extract and print text from a PDF document with stream filtering options."""
    command_instance.execute(
        path=path,
        pages=pages,
        head=head,
        tail=tail,
        grep=grep,
        sed=sed,
        numbered=numbered,
        lines_with=lines_with,
    )


def entry() -> None:
    """Standalone console entry point for dt-ppdf."""
    typer.run(print_pdf_command)
