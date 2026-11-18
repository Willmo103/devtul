"""
YouTube downloader, metadata extractor, and subtitle transcript retriever for DevTul.
Supports video ID extraction from all URL variants, yt-dlp metadata extraction,
transcript retrieval, adaptive stream muxing, and filesystem sanitization.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

from pydantic import BaseModel, Field


class YouTubeVideoMetadata(BaseModel):
    """Structured YouTube video metadata."""

    video_id: str
    url: str
    title: str
    creator: str
    channel_id: Optional[str] = None
    duration: Optional[int] = None
    view_count: Optional[int] = None
    description: Optional[str] = None
    upload_date: Optional[str] = None
    thumbnail_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    has_transcript: bool = False
    transcript: Optional[str] = None


class VideoDownloadResult(BaseModel):
    """Result of a video download operation."""

    video_id: str
    url: str
    local_path: str
    filename: str
    file_size_bytes: int
    duration_seconds: Optional[int] = None
    already_existed: bool = False
    metadata: Optional[YouTubeVideoMetadata] = None


def extract_youtube_video_id(url_or_id: str) -> Optional[str]:
    """
    Extracts an 11-character YouTube video ID from various link structures
    or raw video ID strings.
    """
    if not url_or_id:
        return None

    target = str(url_or_id).strip()

    # Exact 11-character ID (when not a URL)
    if (
        "://" not in target
        and "/" not in target
        and re.fullmatch(r"[a-zA-Z0-9_-]{11}", target)
    ):
        return target

    # URL formats
    try:
        parsed = urlparse(target)
        hostname = (parsed.hostname or "").lower()
        if hostname not in (
            "youtu.be",
            "www.youtu.be",
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "music.youtube.com",
        ):
            return None

        if hostname in ("youtu.be", "www.youtu.be"):
            path_part = parsed.path.lstrip("/").split("/")[0]
            if len(path_part) == 11:
                return path_part
        if hostname in (
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "music.youtube.com",
        ):
            if parsed.path == "/watch":
                v = parse_qs(parsed.query).get("v", [None])[0]
                if v and len(v) == 11:
                    return v
            if parsed.path.startswith(("/embed/", "/v/", "/shorts/", "/live/")):
                parts = parsed.path.strip("/").split("/")
                if len(parts) >= 2 and len(parts[1]) == 11:
                    return parts[1]
    except Exception:
        pass

    return None


def sanitize_filename(name: str, max_length: int = 120) -> str:
    """Replaces filesystem-illegal characters with underscores and limits length."""
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", name)
    sanitized = re.sub(r"[\s_]+", "_", sanitized).strip("_")
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip("_")
    return sanitized or "youtube_video"


def format_timestamp(seconds: float) -> str:
    """Formats seconds into [HH:MM:SS] or [MM:SS]."""
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    if hours > 0:
        return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"
    return f"[{minutes:02d}:{secs:02d}]"


class YouTubeDownloader:
    """YouTube downloader wrapping yt-dlp and YouTubeTranscriptApi."""

    DEFAULT_FORMAT = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    DEFAULT_AUDIO_FORMAT = "bestaudio[ext=m4a]/bestaudio/best"

    def __init__(self, output_dir: Optional[Path] = None, quiet: bool = True):
        self.output_dir = Path(output_dir).resolve() if output_dir else Path.cwd()
        self.quiet = quiet

    def get_transcript(self, video_id: str) -> Optional[str]:
        """Fetches subtitle transcript text with timestamps."""
        if YouTubeTranscriptApi is None:
            return None

        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(
                video_id, languages=["en"]
            )
            lines = []
            for item in transcript_list:
                start_time = format_timestamp(item.get("start", 0))
                text = item.get("text", "").strip()
                if text:
                    lines.append(f"{start_time} {text}")
            return "\n".join(lines) if lines else None
        except Exception:
            # Fallback to any available language
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                lines = []
                for item in transcript_list:
                    start_time = format_timestamp(item.get("start", 0))
                    text = item.get("text", "").strip()
                    if text:
                        lines.append(f"{start_time} {text}")
                return "\n".join(lines) if lines else None
            except Exception:
                return None

    def get_metadata(
        self, url_or_id: str, fetch_transcript: bool = False
    ) -> YouTubeVideoMetadata:
        """Extracts structured video metadata via yt-dlp without downloading media."""
        if yt_dlp is None:
            raise RuntimeError("yt-dlp is required. Install with: pip install yt-dlp")

        video_id = extract_youtube_video_id(url_or_id)
        target_url = (
            f"https://www.youtube.com/watch?v={video_id}" if video_id else url_or_id
        )

        ydl_opts: Dict[str, Any] = {
            "quiet": self.quiet,
            "no_warnings": True,
            "extract_flat": False,
            "skip_download": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=False)
            if not info:
                raise RuntimeError(
                    f"Could not retrieve video information for: {url_or_id}"
                )

        v_id = info.get("id") or video_id or "unknown"
        transcript_text = self.get_transcript(v_id) if fetch_transcript else None

        return YouTubeVideoMetadata(
            video_id=v_id,
            url=f"https://www.youtube.com/watch?v={v_id}",
            title=info.get("title") or "Unknown Title",
            creator=info.get("uploader") or info.get("channel") or "Unknown Creator",
            channel_id=info.get("channel_id"),
            duration=info.get("duration"),
            view_count=info.get("view_count"),
            description=info.get("description"),
            upload_date=info.get("upload_date"),
            thumbnail_url=info.get("thumbnail"),
            tags=info.get("tags") or [],
            has_transcript=transcript_text is not None,
            transcript=transcript_text,
        )

    def download(
        self,
        url_or_id: str,
        target_path: Optional[Path] = None,
        audio_only: bool = False,
        format_selector: Optional[str] = None,
        overwrite: bool = False,
    ) -> VideoDownloadResult:
        """
        Downloads a YouTube video or audio stream into target_path.
        """
        if yt_dlp is None:
            raise RuntimeError("yt-dlp is required. Install with: pip install yt-dlp")

        video_id = extract_youtube_video_id(url_or_id)
        target_url = (
            f"https://www.youtube.com/watch?v={video_id}" if video_id else url_or_id
        )

        # Determine target file / directory
        if target_path:
            p = Path(target_path).resolve()
            if p.is_dir() or str(target_path).endswith(("\\", "/")):
                out_dir = p
                out_tmpl = str(out_dir / "%(title)s [%(id)s].%(ext)s")
            else:
                out_dir = p.parent
                out_tmpl = str(p.with_suffix(".%(ext)s"))
        else:
            out_dir = self.output_dir
            out_tmpl = str(out_dir / "%(title)s [%(id)s].%(ext)s")

        out_dir.mkdir(parents=True, exist_ok=True)

        chosen_format = (
            format_selector
            if format_selector
            else (self.DEFAULT_AUDIO_FORMAT if audio_only else self.DEFAULT_FORMAT)
        )

        ydl_opts: Dict[str, Any] = {
            "format": chosen_format,
            "outtmpl": out_tmpl,
            "quiet": self.quiet,
            "no_warnings": True,
            "overwrites": overwrite,
        }

        if audio_only:
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                    "preferredquality": "192",
                }
            ]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=True)
            if not info:
                raise RuntimeError(f"Could not download video: {url_or_id}")
            downloaded_file = ydl.prepare_filename(info)

        downloaded_path = Path(downloaded_file)
        if not downloaded_path.exists():
            # Check if postprocessor changed extension (e.g. .m4a)
            matches = list(out_dir.glob(f"{downloaded_path.stem}.*"))
            if matches:
                downloaded_path = matches[0]

        # If user explicitly passed exact filename (e.g. out.mp4 or out.m4a) and not dir:
        if target_path and not (
            Path(target_path).is_dir() or str(target_path).endswith(("\\", "/"))
        ):
            final_target = Path(target_path).resolve()
            if downloaded_path.exists() and downloaded_path != final_target:
                if final_target.exists() and overwrite:
                    final_target.unlink()
                if not final_target.exists():
                    downloaded_path.rename(final_target)
                    downloaded_path = final_target

        size = downloaded_path.stat().st_size if downloaded_path.exists() else 0
        v_id = info.get("id") or video_id or "unknown"

        return VideoDownloadResult(
            video_id=v_id,
            url=f"https://www.youtube.com/watch?v={v_id}",
            local_path=str(downloaded_path.as_posix()),
            filename=downloaded_path.name,
            file_size_bytes=size,
            duration_seconds=info.get("duration"),
            already_existed=False,
        )
