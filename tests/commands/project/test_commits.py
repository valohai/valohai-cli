import requests_mock

from tests.fixtures.data import EXECUTION_DETAIL_DATA, PROJECT_DATA
from valohai_cli.commands.project.commits import commits


def test_commits(runner, logged_in_and_linked):
    with requests_mock.mock() as m:
        commit_data = EXECUTION_DETAIL_DATA["commit"]
        m.get(
            f"https://app.valohai.com/api/v0/projects/{PROJECT_DATA['id']}/commits/",
            json=[commit_data],
        )
        result = runner.invoke(commits)
        assert commit_data["ref"] in result.output
        assert commit_data["identifier"] in result.output
