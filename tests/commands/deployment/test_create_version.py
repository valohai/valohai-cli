import uuid

import pytest

from tests.commands.run_test_utils import RunAPIMock
from valohai_cli.commands.deployment.create_version import create_version
from valohai_cli.ctx import get_project
from valohai_cli.models.project import Project


@pytest.mark.parametrize('name', (None, '666'))
def test_create_version(runner, logged_in_and_linked, monkeypatch, name):
    commit_identifier = 'f' * 16

    def mock_resolve_commit(mock_self, *, commit_identifier):
        return {'identifier': commit_identifier}

    monkeypatch.setattr(Project, 'resolve_commit', mock_resolve_commit)

    project = get_project()
    apimock_kwargs = {'deployment_version_name': name} if name else {}
    apimock = RunAPIMock(project.id, commit_identifier, **apimock_kwargs)
    args = ['-d', 'main-deployment', '-e', 'greet', '-c', commit_identifier]
    if name:
        args.extend(['-n', name])

    with apimock:
        # No matching deployment?
        output = runner.invoke(create_version, ['-d', 'not-found-deployment', '-e', 'greet', '-c', commit_identifier]).output
        assert '"not-found-deployment" is not a known deployment (try one of main-deployment)' in output

        output = runner.invoke(create_version, args).output
        assert 'Success!' in output

    # Endpoint with required files
    endpoint = 'predict-digit'
    args = ['-d', 'main-deployment', '-e', endpoint, '-c', commit_identifier]
    if name:
        args.extend(['-n', name])
    with apimock:
        output = runner.invoke(create_version, args).output
        assert f'--{endpoint}-model' in output

        args.extend([f'--{endpoint}-model', 'potat.h5'])
        output = runner.invoke(create_version, args).output
        assert "Not valid datum id: potat.h5" in output

        datum_id = str(uuid.uuid4())
        args.extend([f'--{endpoint}-model', datum_id])
        output = runner.invoke(create_version, args).output
        assert 'Success!' in output
