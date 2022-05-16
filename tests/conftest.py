import pytest
from click.testing import CliRunner

from tests.commands.run_test_utils import RunAPIMock
from tests.fixture_data import LOGGED_IN_DATA, PROJECT_DATA
from valohai_cli.settings import settings
from valohai_cli.settings.persistence import Persistence
from valohai_cli.utils import get_project_directory

pytest.register_assert_rewrite("tests.commands.execution.run_test_utils")


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


@pytest.fixture()
def default_run_api_mock():
    with RunAPIMock(PROJECT_DATA['id'], 'f' * 16, {}) as am:
        yield am
