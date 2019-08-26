import datetime
import json
import re

import pytest
import requests_mock
from click.testing import CliRunner

from tests.fixture_data import CONFIG_DATA, EXECUTION_DATA, PROJECT_DATA, CONFIG_YAML
from valohai_cli import git
from valohai_cli.commands.execution.run import run
from valohai_cli.ctx import get_project
from valohai_cli.utils import get_random_string


class RunAPIMock(requests_mock.Mocker):

    def __init__(self, project_id, commit_id='f' * 16, additional_payload_values=None):
        super(RunAPIMock, self).__init__()
        self.project_id = project_id
        self.commit_id = commit_id
        self.additional_payload_values = (additional_payload_values or {})
        self.get(
            'https://app.valohai.com/api/v0/projects/{}/'.format(project_id),
            json=self.handle_project,
        )
        self.get(
            'https://app.valohai.com/api/v0/projects/{}/commits/'.format(project_id),
            json=self.handle_commits,
        )
        self.get(
            re.compile(r'^https://app.valohai.com/api/v0/commits/(?P<id>.+)/(?:\?.*)?$'),
            json=self.handle_commit_detail,
        )
        self.get(
            re.compile(r'^https://app.valohai.com/api/v0/commits/(?:\?.*)$'),
            json=self.handle_commits_list,
        )
        self.post(
            'https://app.valohai.com/api/v0/executions/',
            json=self.handle_create_execution,
        )
        self.post(
            'https://app.valohai.com/api/v0/projects/{}/import-package/'.format(project_id),
            json=self.handle_create_commit,
        )

    def handle_project(self, request, context):
        return {
            'id': self.project_id,
            'name': 'Project %s' % self.project_id,
        }

    def handle_commits_list(self, request, context):
        return {
            'results': self.handle_commits(request, context),
        }

    def handle_commits(self, request, context):
        commit_obj = self.handle_commit_detail(request, context)
        commit_obj.pop('config', None)  # This wouldn't be in the list response
        return [commit_obj]

    def handle_commit_detail(self, request, context):
        return {
            'identifier': self.commit_id,
            'commit_time': datetime.datetime.now().isoformat(),
            'url': '/api/v0/commits/%s/' % self.commit_id,
            'config': CONFIG_DATA,
        }

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


class RunTestSetup:
    def __init__(self, monkeypatch, adhoc, step_name='train'):
        self.adhoc = adhoc
        self.project_id = PROJECT_DATA['id']
        self.commit_id = 'f' * 40
        monkeypatch.setattr(git, 'get_current_commit', lambda dir: self.commit_id)

        with open(get_project().get_config_filename(), 'w') as yaml_fp:
            yaml_fp.write(CONFIG_YAML)

        self.args = [step_name]
        if adhoc:
            self.args.insert(0, '--adhoc')
        self.values = {}

    def run(self):
        with RunAPIMock(self.project_id, self.commit_id, self.values):
            output = CliRunner().invoke(run, self.args, catch_exceptions=False).output
            # Making sure that non-adhoc executions don't turn adhoc or vice versa.
            assert ('Uploaded ad-hoc code' in output) == self.adhoc
            assert '#{counter}'.format(counter=EXECUTION_DATA['counter']) in output


@pytest.fixture(params=['regular', 'adhoc'], ids=('regular', 'adhoc'))
def run_test_setup(request, logged_in_and_linked, monkeypatch):
    return RunTestSetup(monkeypatch=monkeypatch, adhoc=(request.param == 'adhoc'))
