import os

import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


@pytest.mark.trylast
def pytest_configure(config):
    config_dir = config._tmpdirhandler.mktemp('valohai-cli-cfg', numbered=True)
    os.environ.setdefault('VALOHAI_CONFIG_DIR', str(config_dir))
