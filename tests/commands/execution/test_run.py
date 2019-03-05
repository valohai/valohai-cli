import json

import pytest
import requests_mock

from tests.fixture_data import CONFIG_YAML, EXECUTION_DATA, PROJECT_DATA
from valohai_cli import git
from valohai_cli.commands.execution.run import run
from valohai_cli.ctx import get_project
from valohai_cli.utils import get_random_string


class RunAPIMock(requests_mock.Mocker):

    def __init__(self, project_id, commit_id, additional_payload_values):
        super(RunAPIMock, self).__init__()
        self.project_id = project_id
        self.commit_id = commit_id
        self.additional_payload_values = additional_payload_values
        self.get(
            'https://app.valohai.com/api/v0/projects/{}/commits/'.format(project_id),
            json=self.handle_commits,
        )
        self.post(
            'https://app.valohai.com/api/v0/executions/',
            json=self.handle_create_execution,
        )
        self.post(
            'https://app.valohai.com/api/v0/projects/{}/import-package/'.format(project_id),
            json=self.handle_create_commit,
        )

    def handle_commits(self, request, context):
        return [{'identifier': self.commit_id}]

    def handle_create_execution(self, request, context):
        body_json = json.loads(request.body.decode('utf-8'))
        assert body_json['project'] == self.project_id
        assert body_json['step'] == 'Train model'
        assert body_json['commit'] == self.commit_id
        for key, value in self.additional_payload_values.items():
            assert body_json[key] == value
        context.status_code = 201
        return EXECUTION_DATA.copy()

    def handle_create_commit(self, request, context):
        assert request.body
        commit_id = "~%s" % get_random_string()
        self.commit_id = commit_id  # Only accept the new commit
        return {
            'repository': '8',
            'identifier': commit_id,
            'ref': 'adhoc',
            'ctime': '2017-03-09T14:56:53.875721Z',
            'commit_time': '2017-03-09T14:56:53.875475Z',
        }


def test_run_requires_step(runner, logged_in_and_linked):
    assert 'Missing argument' in runner.invoke(run, catch_exceptions=False).output


@pytest.mark.parametrize('pass_param', (False, True))
@pytest.mark.parametrize('pass_input', (False, True))
@pytest.mark.parametrize('pass_env', (False, True))
@pytest.mark.parametrize('adhoc', (False, True), ids=('regular', 'adhoc'))
def test_run(runner, logged_in_and_linked, monkeypatch, pass_param, pass_input, pass_env, adhoc):
    project_id = PROJECT_DATA['id']
    commit_id = 'f' * 40
    monkeypatch.setattr(git, 'get_current_commit', lambda dir: commit_id)

    with open(get_project().get_config_filename(), 'w') as yaml_fp:
        yaml_fp.write(CONFIG_YAML)

    args = ['train']
    if adhoc:
        args.insert(0, '--adhoc')

    values = {}
    if pass_param:
        args.append('--max-steps=1801')
        values['parameters'] = {'max_steps': 1801}

    if pass_input:
        args.append('--in1=http://url')
        args.append('--in1=http://anotherurl')
        values['inputs'] = {'in1': ['http://url', 'http://anotherurl']}

    if pass_env:
        args.append('--environment=015dbd56-2670-b03e-f37c-dc342714f1b5')
        values['environment'] = '015dbd56-2670-b03e-f37c-dc342714f1b5'

    with RunAPIMock(project_id, commit_id, values):
        output = runner.invoke(run, args, catch_exceptions=False).output
        if adhoc:
            assert 'Uploaded ad-hoc code' in output
        else:
            # Making sure that non-adhoc executions don't turn adhoc.
            assert 'Uploaded ad-hoc code' not in output
        assert '#{counter}'.format(counter=EXECUTION_DATA['counter']) in output


def test_param_type_validation(runner, logged_in_and_linked):
    with open(get_project().get_config_filename(), 'w') as yaml_fp:
        yaml_fp.write(CONFIG_YAML)
    rv = runner.invoke(run, ['train', '--max-steps=plonk'], catch_exceptions=False)
    assert 'plonk is not a valid integer' in rv.output


def test_run_no_git(runner, logged_in_and_linked):
    project_id = PROJECT_DATA['id']

    with open(get_project().get_config_filename(), 'w') as yaml_fp:
        yaml_fp.write(CONFIG_YAML)

    args = ['train']

    with RunAPIMock(project_id, None, {}):
        output = runner.invoke(run, args, catch_exceptions=False).output
        assert 'is not a Git repository' in output


def test_param_input_sanitization(runner, logged_in_and_linked):
    with open(get_project().get_config_filename(), 'w') as yaml_fp:
        yaml_fp.write('''
- step:
    name: Train model
    image: busybox
    command: "false"
    inputs:
      - name: Ridiculously Complex Input_Name
        default: http://example.com/
    parameters:
      - name: Parameter With Highly Convoluted Name
        pass-as: --simple={v}
        type: integer
        default: 1
''')
    output = runner.invoke(run, ['train', '--help'], catch_exceptions=False).output
    assert '--Parameter-With-Highly-Convoluted-Name' in output
    assert '--parameter-with-highly-convoluted-name' in output
    assert '--Ridiculously-Complex-Input-Name' in output
    assert '--ridiculously-complex-input-name' in output


def test_typo_check(runner, logged_in_and_linked):
    with open(get_project().get_config_filename(), 'w') as yaml_fp:
        yaml_fp.write(CONFIG_YAML)
    args = ['train', '--max-setps=80']  # Oopsy!
    output = runner.invoke(run, args, catch_exceptions=False).output
    assert '(Possible options:' in output or 'Did you mean' in output
    assert '--max-steps' in output
