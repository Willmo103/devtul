"""
Command 'dt yt' / 'dt-yt'.
Downloads YouTube video, audio stream, and/or retrieves subtitle transcripts.
Usage: dt yt <url> <filepath> [-t --trans [pth] | -a --audio [path]]
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from rich.console import Console
import typer
from typer.core import TyperCommand

from devtul.core.youtube_downloader import (
    YouTubeDownloader,
    extract_youtube_video_id,
)

console = Console()


def normalize_yt_args(args: List[str]) -> List[str]:
    """
    Normalizes flags like '-t' / '--trans' and '-a' / '--audio' so they can
    either take an optional path or act as a flag value ('__AUTO__').
    """
    new_args: List[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("-t", "--trans", "--transcript") or arg in (
            "-a",
            "--audio",
            "--audio-only",
        ):
            new_args.append(arg)
            # Check if next token is a value (does not start with '-')
            if i + 1 < len(args) and not args[i + 1].startswith("-"):
                new_args.append(args[i + 1])
                i += 2
                continue
            else:
                new_args.append("__AUTO__")
                i += 1
                continue
        new_args.append(arg)
        i += 1
    return new_args


class YtCommand(TyperCommand):
    """Custom TyperCommand that normalizes optional-value flags for 'dt yt'."""

    def parse_args(self, ctx: typer.Context, args: List[str]) -> List[str]:
        return super().parse_args(ctx, normalize_yt_args(args))


yt_app = typer.Typer(
    name="yt",
    help="Download YouTube video, audio, or subtitle transcripts.",
    no_args_is_help=True,
)


@yt_app.command(cls=YtCommand, name="download")
def yt_command(
    url: str = typer.Argument(..., help="YouTube URL or 11-char video ID."),
    filepath: Path = typer.Argument(
        ...,
        help="Target file path or directory for download (e.g. video.mp4, audio.m4a).",
    ),
    trans: Optional[str] = typer.Option(
        None,
        "--trans",
        "-t",
        help="Extract subtitle transcript (optional custom path to save transcript).",
    ),
    audio: Optional[str] = typer.Option(
        None,
        "--audio",
        "-a",
        help="Download high-quality audio stream only (optional custom path).",
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite existing media and transcript files."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Display verbose yt-dlp logger output."
    ),
) -> None:
    """
    Download a YouTube video, audio stream, or extract subtitle transcript.
    Examples:
        dt yt https://youtu.be/dQw4w9WgXcQ video.mp4
        dt yt https://youtu.be/dQw4w9WgXcQ audio.m4a -a
        dt yt https://youtu.be/dQw4w9WgXcQ video.mp4 -t
        dt yt https://youtu.be/dQw4w9WgXcQ video.mp4 -t transcript.txt
        dt yt https://youtu.be/dQw4w9WgXcQ audio.m4a -a -t sub.txt
    """
    video_id = extract_youtube_video_id(url)
    if not video_id:
        console.print(
            f"[bold red]Error:[/bold red] Invalid YouTube URL or video ID: '{url}'"
        )
        raise typer.Exit(code=1)

    downloader = YouTubeDownloader(quiet=not verbose)

    # 1. Handle Transcript if requested (-t / --trans)
    if trans is not None:
        if trans == "__AUTO__":
            trans_path = filepath.with_suffix(".txt")
        else:
            trans_path = Path(trans).resolve()

        console.print(f"[cyan]Fetching transcript for video {video_id}...[/cyan]")
        transcript_text = downloader.get_transcript(video_id)
        if transcript_text:
            trans_path.parent.mkdir(parents=True, exist_ok=True)
            trans_path.write_text(transcript_text, encoding="utf-8")
            console.print(f"[bold green]Transcript saved:[/bold green] {trans_path}")
        else:
            console.print(
                "[yellow]Warning: No subtitle transcript available for this video.[/yellow]"
            )

    # 2. Determine whether media download is audio-only or video
    is_audio = audio is not None

    if is_audio:
        if audio != "__AUTO__":
            target_media_path = Path(audio).resolve()
        else:
            target_media_path = filepath.resolve()
        console.print(f"[cyan]Downloading audio stream for {video_id}...[/cyan]")
    else:
        target_media_path = filepath.resolve()
        console.print(f"[cyan]Downloading video for {video_id}...[/cyan]")

    try:
        result = downloader.download(
            url_or_id=url,
            target_path=target_media_path,
            audio_only=is_audio,
            overwrite=overwrite,
        )
        size_mb = round(result.file_size_bytes / (1024 * 1024), 2)
        console.print(
            f"[bold green]Successfully downloaded:[/bold green] {result.local_path} ({size_mb} MB)"
        )
    except Exception as e:
        console.print(f"[bold red]Error downloading {url}:[/bold red] {e}")
        raise typer.Exit(code=1)


def entry():
    import sys

    # If the user invokes `dt-yt <url> <filepath> ...`, route directly
    if (
        len(sys.argv) > 1
        and not sys.argv[1].startswith("-")
        and sys.argv[1] != "download"
    ):
        sys.argv.insert(1, "download")
    yt_app()
