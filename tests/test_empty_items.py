import os
from pathlib import Path
from typer.testing import CliRunner

from devtul.commands.empty_items import empty
from devtul.main import app

runner = CliRunner()


def test_empty_files_subcommand_full_path(tmp_path: Path):
    empty_file = tmp_path / "empty_file.txt"
    empty_file.write_text("")
    non_empty = tmp_path / "non_empty.txt"
    non_empty.write_text("content")

    # Run `dt empty files <path>`
    result = runner.invoke(empty, ["files", str(tmp_path), "--no-git"])
    assert result.exit_code == 0
    expected_full_path = empty_file.resolve().as_posix()
    assert expected_full_path in result.output
    assert non_empty.name not in result.output


def test_empty_dirs_and_folders_subcommand_full_path(tmp_path: Path):
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    non_empty_dir = tmp_path / "non_empty_dir"
    non_empty_dir.mkdir()
    (non_empty_dir / "child.txt").write_text("data")

    expected_full_path = empty_dir.resolve().as_posix()

    # Test `dirs` subcommand
    res_dirs = runner.invoke(empty, ["dirs", str(tmp_path)])
    assert res_dirs.exit_code == 0
    assert expected_full_path in res_dirs.output
    assert non_empty_dir.name not in res_dirs.output

    # Test `folders` alias subcommand
    res_folders = runner.invoke(empty, ["folders", str(tmp_path)])
    assert res_folders.exit_code == 0
    assert expected_full_path in res_folders.output
    assert non_empty_dir.name not in res_folders.output


def test_empty_flags_on_empty_command(tmp_path: Path):
    empty_file = tmp_path / "empty_flag_file.txt"
    empty_file.write_text("")
    empty_dir = tmp_path / "empty_flag_dir"
    empty_dir.mkdir()

    expected_file_path = empty_file.resolve().as_posix()
    expected_dir_path = empty_dir.resolve().as_posix()

    # 1. dt empty --files --path <path>
    res_files = runner.invoke(empty, ["--files", "--path", str(tmp_path), "--no-git"])
    assert res_files.exit_code == 0
    assert expected_file_path in res_files.output
    assert expected_dir_path not in res_files.output

    # 2. dt empty --folders --path <path>
    res_folders = runner.invoke(empty, ["--folders", "--path", str(tmp_path)])
    assert res_folders.exit_code == 0
    assert expected_dir_path in res_folders.output
    assert expected_file_path not in res_folders.output

    # 3. dt empty --dirs -p <path>
    res_dirs = runner.invoke(empty, ["--dirs", "-p", str(tmp_path)])
    assert res_dirs.exit_code == 0
    assert expected_dir_path in res_dirs.output


def test_empty_flags_via_main_app(tmp_path: Path):
    empty_file = tmp_path / "app_empty.txt"
    empty_file.write_text("")
    empty_dir = tmp_path / "app_empty_dir"
    empty_dir.mkdir()

    expected_file_path = empty_file.resolve().as_posix()
    expected_dir_path = empty_dir.resolve().as_posix()

    # dt empty --files -p <path> via main devtul app
    res_files = runner.invoke(
        app, ["empty", "--files", "-p", str(tmp_path), "--no-git"]
    )
    assert res_files.exit_code == 0
    assert expected_file_path in res_files.output

    # dt empty --folders -p <path> via main devtul app
    res_folders = runner.invoke(app, ["empty", "--folders", "-p", str(tmp_path)])
    assert res_folders.exit_code == 0
    assert expected_dir_path in res_folders.output


def test_empty_flags_default_to_cwd(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cwd_empty_file = tmp_path / "cwd_empty.txt"
    cwd_empty_file.write_text("")
    cwd_empty_dir = tmp_path / "cwd_empty_folder"
    cwd_empty_dir.mkdir()

    expected_file = cwd_empty_file.resolve().as_posix()
    expected_dir = cwd_empty_dir.resolve().as_posix()

    res_f = runner.invoke(empty, ["--files", "--no-git"])
    assert res_f.exit_code == 0
    assert expected_file in res_f.output

    res_d = runner.invoke(empty, ["--folders"])
    assert res_d.exit_code == 0
    assert expected_dir in res_d.output


def test_empty_json_yaml_csv_formatting(tmp_path: Path):
    empty_file = tmp_path / "data.txt"
    empty_file.write_text("")
    expected_path = empty_file.resolve().as_posix()

    # JSON output
    res_json = runner.invoke(empty, ["files", str(tmp_path), "--json", "--no-git"])
    assert res_json.exit_code == 0
    cleaned_json = res_json.output.strip()
    assert expected_path in cleaned_json

    # YAML output
    res_yaml = runner.invoke(empty, ["files", str(tmp_path), "--yaml", "--no-git"])
    assert res_yaml.exit_code == 0
    assert f"- {expected_path}" in res_yaml.output

    # CSV output
    res_csv = runner.invoke(empty, ["files", str(tmp_path), "--csv", "--no-git"])
    assert res_csv.exit_code == 0
    assert f"'{expected_path}'" in res_csv.output

    # Dirs JSON output
    empty_dir = tmp_path / "empty_sub"
    empty_dir.mkdir()
    expected_dir_path = empty_dir.resolve().as_posix()

    res_dir_json = runner.invoke(empty, ["dirs", str(tmp_path), "--json"])
    assert res_dir_json.exit_code == 0
    assert expected_dir_path in res_dir_json.output

    # Dirs YAML output
    res_dir_yaml = runner.invoke(empty, ["dirs", str(tmp_path), "--yaml"])
    assert res_dir_yaml.exit_code == 0
    assert f"- {expected_dir_path}" in res_dir_yaml.output


def test_empty_no_args_shows_help():
    res = runner.invoke(empty, [])
    assert res.exit_code == 0
    assert "Locate empty files and folders" in res.output
    assert "--files" in res.output
    assert "--folders" in res.output


def test_empty_nonexistent_path():
    nonexistent = Path("nonexistent_path_xyz123_devtul")
    res = runner.invoke(empty, ["--files", "-p", str(nonexistent)])
    assert res.exit_code == 1
    assert "does not exist" in res.output
