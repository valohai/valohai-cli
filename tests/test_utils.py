import os

import pytest
import sys

from valohai_cli.utils import walk_directory_parents


def test_dir_parents():
    if sys.platform == 'win32':
        pytest.skip('not sure how to test on win32 at present')
    dir = os.path.dirname(__file__)
    dirs = list(walk_directory_parents(dir))
    assert dirs[0] == dir
    assert dirs[-1] == '/'
