"""
Tests for StringsCommand ('dt str').
"""

from pathlib import Path
import pytest

from devtul.commands.strings_cmd import StringsCommand, extract_printable_strings


def test_extract_printable_strings(tmp_path):
    # Binary file with nulls and printable sequences
    bin_file = tmp_path / "sample.bin"
    content = b"\x00\x00\x01\x02Hello_World\x00\x00\x05sh\x00LongerValidString123\x00"
    bin_file.write_bytes(content)

    # min_len=4 should capture Hello_World and LongerValidString123, but not 'sh'
    strings_4 = extract_printable_strings(bin_file, min_len=4)
    assert "Hello_World" in strings_4
    assert "LongerValidString123" in strings_4
    assert "sh" not in strings_4

    # min_len=2 should capture 'sh' as well
    strings_2 = extract_printable_strings(bin_file, min_len=2)
    assert "sh" in strings_2


def test_strings_command_execution(tmp_path):
    bin_file = tmp_path / "sample.dat"
    bin_file.write_bytes(b"\x00alpha_test\x00\x00beta_test\x00\x00gamma_run\x00")

    cmd = StringsCommand()
    res = cmd.execute(path=bin_file, min_len=4, grep="test")
    assert res.total_lines == 2
    assert "alpha_test" in res.lines
    assert "beta_test" in res.lines
    assert "gamma_run" not in res.lines
