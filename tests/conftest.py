import pytest
from click.testing import CliRunner

from tests.commands.run_test_utils import RunAPIMock
from tests.fixture_data import LOGGED_IN_DATA, PROJECT_DATA
from tests.stub_git import StubGit
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


class PedanticCliRunner(CliRunner):
    """Override runner.invoke() to let any raised exceptions bubble through,
    as the default is to catch it.

    Tests can explicitly check exit status if the command failed due to an uncaught exception,
    but they generally do not do this.
    """
    def invoke(self, *args, **kwargs):
        catch_exceptions = kwargs.pop("catch_exceptions", None)
        # This flips the default to False
        catch_exceptions = catch_exceptions is not None
        return super().invoke(*args, catch_exceptions=catch_exceptions, **kwargs)


@pytest.fixture
def runner():
    return PedanticCliRunner()


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


@pytest.fixture(scope='module')
def stub_git(tmp_path_factory) -> StubGit:
    repository_root = tmp_path_factory.mktemp('stub_git')
    stub = StubGit(repository_root)
    stub.init()
    return stub
