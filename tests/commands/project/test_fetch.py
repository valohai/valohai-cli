import requests_mock

from tests.fixtures.data import EXECUTION_DETAIL_DATA, PROJECT_DATA
from valohai_cli.commands.project.fetch import fetch


def test_fetch(runner, logged_in_and_linked):
    with requests_mock.mock() as m:
        commit_data = EXECUTION_DETAIL_DATA["commit"]
        m.post(
            f"https://app.valohai.com/api/v0/projects/{PROJECT_DATA['id']}/fetch/",
            json={
                "commits": [commit_data],
                "errors": ["oops"],
            },
            status_code=201,
        )
        result = runner.invoke(fetch)
        assert commit_data["ref"] in result.output
        assert commit_data["identifier"] in result.output
