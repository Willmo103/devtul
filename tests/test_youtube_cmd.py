from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from devtul.commands.youtube_cmd import normalize_yt_args, yt_app
from devtul.core.youtube_downloader import (
    VideoDownloadResult,
    extract_youtube_video_id,
    sanitize_filename,
)
from devtul.main import app

runner = CliRunner()


def test_extract_youtube_video_id():
    # 1. Standard watch URL
    assert (
        extract_youtube_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        == "dQw4w9WgXcQ"
    )
    # 2. Short URL
    assert extract_youtube_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    # 3. Shorts URL
    assert (
        extract_youtube_video_id("https://youtube.com/shorts/dQw4w9WgXcQ?feature=share")
        == "dQw4w9WgXcQ"
    )
    # 4. Embed URL
    assert (
        extract_youtube_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ")
        == "dQw4w9WgXcQ"
    )
    # 5. Raw 11-char ID
    assert extract_youtube_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    # 6. Invalid URL
    assert extract_youtube_video_id("https://example.com/not-youtube") is None


def test_sanitize_filename():
    assert sanitize_filename("My Video: Part 1/2? *Cool*") == "My_Video_Part_1_2_Cool"


def test_normalize_yt_args():
    # Flag only without path gets '__AUTO__'
    assert normalize_yt_args(["http://abc", "vid.mp4", "-a"]) == [
        "http://abc",
        "vid.mp4",
        "-a",
        "__AUTO__",
    ]
    # Option with path value keeps path
    assert normalize_yt_args(["http://abc", "vid.mp4", "-a", "audio.m4a"]) == [
        "http://abc",
        "vid.mp4",
        "-a",
        "audio.m4a",
    ]
    # Both flags without paths
    assert normalize_yt_args(["http://abc", "vid.mp4", "-a", "-t"]) == [
        "http://abc",
        "vid.mp4",
        "-a",
        "__AUTO__",
        "-t",
        "__AUTO__",
    ]
    # Both options with custom paths
    assert normalize_yt_args(
        ["http://abc", "vid.mp4", "-a", "aud.m4a", "-t", "sub.txt"]
    ) == ["http://abc", "vid.mp4", "-a", "aud.m4a", "-t", "sub.txt"]


def test_yt_command_execution(tmp_path: Path):
    target_video = tmp_path / "rick.mp4"
    mock_result = VideoDownloadResult(
        video_id="dQw4w9WgXcQ",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        local_path=str(target_video.as_posix()),
        filename="rick.mp4",
        file_size_bytes=1048576,
        duration_seconds=212,
    )

    with (
        patch(
            "devtul.commands.youtube_cmd.YouTubeDownloader.download",
            return_value=mock_result,
        ),
        patch(
            "devtul.commands.youtube_cmd.YouTubeDownloader.get_transcript",
            return_value="[00:01] Never gonna give you up",
        ),
    ):

        # 1. Video download with auto-transcript (-t)
        res = runner.invoke(app, ["yt", "dQw4w9WgXcQ", str(target_video), "-t"])
        assert res.exit_code == 0
        expected_txt = tmp_path / "rick.txt"
        assert expected_txt.exists()
        assert "Never gonna give you up" in expected_txt.read_text(encoding="utf-8")

        # 2. Audio only with custom transcript path
        custom_sub = tmp_path / "custom.txt"
        target_audio = tmp_path / "song.m4a"
        res_audio = runner.invoke(
            app, ["yt", "dQw4w9WgXcQ", str(target_audio), "-a", "-t", str(custom_sub)]
        )
        assert res_audio.exit_code == 0
        assert custom_sub.exists()
        assert "Never gonna give you up" in custom_sub.read_text(encoding="utf-8")
