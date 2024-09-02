import os
import sys

import pytest

from valohai_cli.utils import (
    clean_log_line,
    force_bytes,
    force_text,
    humanize_identifier,
    sanitize_option_name,
    walk_directory_parents,
)
from valohai_cli.utils.matching import match_prefix


def test_dir_parents():
    if sys.platform == "win32":
        pytest.skip("not sure how to test on win32 at present")
    dir = os.path.dirname(__file__)
    dirs = list(walk_directory_parents(dir))
    assert dirs[0] == dir
    assert dirs[-1] == "/"


def test_force_text_and_bytes():
    assert force_text(b"f\xc3\xb6\xc3\xb6") == "föö"
    assert force_bytes("föö", encoding="iso-8859-1") == b"f\xf6\xf6"
    assert force_bytes(8) == b"8"
    assert force_text([]) == "[]"


def test_match_prefix():
    assert match_prefix(["FOO", "BAR"], "foo") == "FOO"
    assert match_prefix(["FOO", "FEE"], "f") is None
    assert match_prefix(["FOO", "FEE"], "f", return_unique=False) == ["FOO", "FEE"]


def test_humanize_identifier():
    assert humanize_identifier("_____Foo-Bar_______") == "Foo Bar"


def test_clean_log_line():
    assert (
        clean_log_line("ls\r\n\x1b[00m\x1b[01;31mexamplefile.zip\x1b[00m\r\n\x1b[01;31m")
        == "ls examplefile.zip"
    )


def test_sanitize_option_name():
    assert sanitize_option_name("Name With  Space") == "Name-With-Space"
    assert sanitize_option_name("Name With Spaces. And Dots.") == "Name-With-Spaces-And-Dots"
    assert sanitize_option_name("äää") == "aaa"
