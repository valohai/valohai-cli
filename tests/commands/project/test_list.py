import requests_mock

from tests.fixture_data import PROJECT_DATA
from valohai_cli.commands.project.list import list


def test_list(runner, logged_in):
    with requests_mock.mock() as m:
        m.get("https://app.valohai.com/api/v0/projects/", json={"results": [PROJECT_DATA]})
        result = runner.invoke(list)
        assert PROJECT_DATA["name"] in result.output
