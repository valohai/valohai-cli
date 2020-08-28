from tests.commands.run_test_utils import RunAPIMock
from tests.fixture_data import PROJECT_DATA
from valohai_cli.commands.execution.run import run
from valohai_cli.models.remote_project import RemoteProject
from valohai_cli.override import configure_project_override, configure_token_login
from valohai_cli.settings import settings

test_token = 'x' * 12


def test_remote_project(request, runner, monkeypatch, tmpdir):
    project_id = PROJECT_DATA['id']
    request.addfinalizer(lambda: settings.reset())
    monkeypatch.chdir(tmpdir)
    with RunAPIMock(project_id, 'f' * 40, {}) as mock:
        configure_token_login(None, test_token)
        configure_project_override(project_id=project_id, mode=None)
        assert isinstance(settings.override_project, RemoteProject)
        # Regular execution
        run_output = runner.invoke(run, ['train'], catch_exceptions=False).output
        assert 'created' in run_output
        assert 'Using remote project' in run_output
        # Ad-hocs don't work
        assert 'can not be used' in runner.invoke(run, ['train', '--adhoc'], catch_exceptions=False).output
