import pytest

from tests.commands.run_test_utils import RunAPIMock
from tests.fixture_data import PROJECT_DATA
from valohai_cli.commands.execution.run import run as exec_run
from valohai_cli.commands.pipeline.run import run as pipeline_run
from valohai_cli.models.remote_project import RemoteProject
from valohai_cli.override import configure_project_override, configure_token_login
from valohai_cli.settings import settings

test_token = 'x' * 12


@pytest.fixture()
def remote_project_setup(request, monkeypatch, tmpdir):
    project_id = PROJECT_DATA['id']
    request.addfinalizer(lambda: settings.reset())
    monkeypatch.chdir(tmpdir)
    with RunAPIMock(project_id, 'f' * 40, {}, num_parameters=2):
        configure_token_login(None, test_token)
        configure_project_override(project_id=project_id, mode=None)
        assert isinstance(settings.override_project, RemoteProject)
        yield


def test_execution_remote_project(remote_project_setup, runner):
    run_output = runner.invoke(exec_run, ['Train model'], catch_exceptions=False).output
    assert 'created' in run_output
    assert 'Using remote project' in run_output


def test_execution_remote_project_adhoc(remote_project_setup, runner):
    # Ad-hocs don't work with remote projects
    run_output = runner.invoke(exec_run, ['Train model', '--adhoc'], catch_exceptions=False).output
    assert 'can not be used' in run_output


def test_pipeline_remote_project(remote_project_setup, runner):
    run_output = runner.invoke(pipeline_run, ['Train Pipeline', f'--commit={"f" * 16}'], catch_exceptions=False).output
    assert 'queued' in run_output
    assert 'Success! Pipeline =' in run_output


def test_pipeline_remote_project_adhoc(remote_project_setup, runner):
    # Ad-hocs don't work with remote projects
    run_output = runner.invoke(pipeline_run, ['Training Pipeline', '--adhoc'], catch_exceptions=False).output
    assert 'can not be used' in run_output
