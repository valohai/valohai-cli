import pytest
from click.testing import CliRunner

from tests.fixture_data import LOGGED_IN_DATA, PROJECT_DATA
from valohai_cli.settings import settings
from valohai_cli.settings.persistence import Persistence
from valohai_cli.utils import get_project_directory


@pytest.fixture
def logged_in(monkeypatch):
    monkeypatch.setattr(settings, 'persistence', Persistence(LOGGED_IN_DATA.copy()))


@pytest.fixture
def logged_in_and_linked(monkeypatch):
    data = dict(
        LOGGED_IN_DATA,
        links={get_project_directory(): PROJECT_DATA}
    )

    monkeypatch.setattr(settings, 'persistence', Persistence(data))


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def isolate_cli(tmpdir, monkeypatch):
    config_dir = str(tmpdir.mkdir('cfg'))
    project_dir = str(tmpdir.mkdir('proj'))
    monkeypatch.setenv('VALOHAI_CONFIG_DIR', config_dir)
    monkeypatch.setenv('VALOHAI_PROJECT_DIR', project_dir)
