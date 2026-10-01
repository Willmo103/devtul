"""
Command 'dt str' / 'dt strings'.
Extracts printable character sequences from binary or text files,
with configurable minimum length and StringCommand stream filtering.
"""

from pathlib import Path
import re
import sys
from typing import Generator, List, Optional

from rich.console import Console
import typer
from typing_extensions import Annotated

from devtul.core.command import StringCommand
from devtul.core.models import StringCommandResult, StringFilterOptions

console = Console()


def extract_printable_strings(
    file_path: Path, min_len: int = 4, chunk_size: int = 1024 * 1024
) -> List[str]:
    """
    Extracts printable ASCII character sequences (bytes 0x20-0x7e plus tab)
    of at least min_len characters from a binary or text file.
    """
    pattern = re.compile(rb"[\x20-\x7e\t]{" + str(min_len).encode() + rb",}")
    extracted: List[str] = []

    with open(file_path, "rb") as f:
        remainder = b""
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                if remainder:
                    for match in pattern.finditer(remainder):
                        extracted.append(match.group().decode("latin-1", errors="replace"))
                break

            data = remainder + chunk
            matches = list(pattern.finditer(data))
            if not matches:
                remainder = data[-min_len:]
                continue

            last_match = matches[-1]
            # Check if last match extends to the end of chunk
            if last_match.end() == len(data):
                for match in matches[:-1]:
                    extracted.append(match.group().decode("latin-1", errors="replace"))
                remainder = last_match.group()
            else:
                for match in matches:
                    extracted.append(match.group().decode("latin-1", errors="replace"))
                remainder = data[last_match.end():]
                if len(remainder) > min_len:

                    remainder = remainder[-min_len:]

    return extracted


class StringsCommand(StringCommand):
    """
    Extracts printable character sequences from binary or text files.
    """

    name: str = "str"
    help: str = "Extract printable character strings from binary, executable, or text files."

    @property
    def usage(self) -> str:
        return "dt str <PATH> [OPTIONS]"

    @property
    def examples(self) -> list[str]:
        return [
            "dt str devtul.exe --min-len 6",
            "dt str library.dll --grep 'kernel32' --numbered",
            "dt str binary.dat --lines-with 'http'",
            "dt str devtul.exe --head 25",
            "dt str data.bin --sed 's/foo/bar/g'",
        ]

    def execute(
        self,
        path: Path,
        min_len: int = 4,
        head: Optional[int] = None,
        tail: Optional[int] = None,
        grep: Optional[str] = None,
        sed: Optional[str] = None,
        numbered: bool = False,
        lines_with: Optional[str] = None,
    ) -> StringCommandResult:
        resolved = path.resolve()
        if not resolved.exists():
            console.print(f"[bold red]Error: File not found at '{resolved}'.[/bold red]")
            raise typer.Exit(code=1)

        try:
            raw_strings = extract_printable_strings(resolved, min_len=min_len)
        except Exception as e:
            console.print(f"[bold red]Error extracting strings from '{resolved}': {e}[/bold red]")
            raise typer.Exit(code=1)

        options = StringFilterOptions(
            head=head,
            tail=tail,
            grep=grep,
            sed=sed,
            numbered=numbered,
            lines_with=lines_with,
        )

        filtered_lines = self.process_lines(raw_strings, options)
        self.render_console(filtered_lines, options, console=console)

        return StringCommandResult(
            command_name="str",
            lines=filtered_lines,
            total_lines=len(filtered_lines),
        )


command_instance = StringsCommand()


def strings_command(
    path: Annotated[Path, typer.Argument(help="Path to the file to extract strings from.")],
    min_len: Annotated[
        int,
        typer.Option(
            "--min-len",
            "-m",
            help="Minimum string length to extract (default: 4).",
        ),
    ] = 4,
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
            "-N",
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
    """Extract printable strings from a file with stream filtering options."""
    command_instance.execute(
        path=path,
        min_len=min_len,
        head=head,
        tail=tail,
        grep=grep,
        sed=sed,
        numbered=numbered,
        lines_with=lines_with,
    )


def entry() -> None:
    """Standalone console entry point for dt-str."""
    typer.run(strings_command)
