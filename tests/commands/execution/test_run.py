import json

import pytest
import requests_mock

from tests.fixture_data import PROJECT_DATA, CONFIG_YAML
from valohai_cli import git
from valohai_cli.commands.execution.run import run
from valohai_cli.ctx import get_project


def get_test_run_requests_mock(project_id, commit_id, additional_payload_values):
    m = requests_mock.mock()
    m.get('https://app.valohai.com/api/v0/projects/{}/commits/'.format(project_id), json=[
        {
            'identifier': commit_id,
        },
    ])

    def handle_create_execution(request, context):
        body_json = json.loads(request.body.decode('utf-8'))
        assert body_json['project'] == project_id
        assert body_json['step'] == 'Train model'
        assert body_json['commit'] == commit_id
        for key, value in additional_payload_values.items():
            assert body_json[key] == value
        context.status_code = 201
        return {
            'id': 1337,
            'counter': 1337,
            'link': '/',
        }

    m.post('https://app.valohai.com/api/v0/executions/', json=handle_create_execution)

    return m


def test_run_requires_step(runner, logged_in_and_linked):
    assert 'Missing argument' in runner.invoke(run, catch_exceptions=False).output


@pytest.mark.parametrize('pass_param', (False, True))
@pytest.mark.parametrize('pass_input', (False, True))
def test_run(runner, logged_in_and_linked, monkeypatch, pass_param, pass_input):
    project_id = PROJECT_DATA['id']
    commit_id = 'f' * 40
    monkeypatch.setattr(git, 'get_current_commit', lambda dir: commit_id)

    with open(get_project().get_config_filename(), 'w') as yaml_fp:
        yaml_fp.write(CONFIG_YAML)

    args = ['train']
    values = {}
    if pass_param:
        args.append('--max-steps=1801')
        values['parameters'] = {'max_steps': 1801}

    if pass_input:
        args.append('--in1=http://url')
        values['inputs'] = {'in1': 'http://url'}

    with get_test_run_requests_mock(project_id, commit_id, values):
        output = runner.invoke(run, args, catch_exceptions=False).output
        assert '#1337' in output


def test_param_type_validation(runner, logged_in_and_linked):
    with open(get_project().get_config_filename(), 'w') as yaml_fp:
        yaml_fp.write(CONFIG_YAML)
    rv = runner.invoke(run, ['train', '--max-steps=plonk'], catch_exceptions=False)
    assert 'plonk is not a valid integer' in rv.output
