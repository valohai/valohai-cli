import requests_mock

from tests.fixtures.data import EXECUTION_DETAIL_DATA
from valohai_cli.commands.execution.list import list


def test_list(runner, logged_in_and_linked):
    with requests_mock.mock() as m:
        m.get(
            "https://app.valohai.com/api/v0/executions/",
            json={
                "results": [
                    EXECUTION_DETAIL_DATA,
                    EXECUTION_DETAIL_DATA,
                    EXECUTION_DETAIL_DATA,
                ],
            },
        )

        output = runner.invoke(list, catch_exceptions=False).output
        assert output.count("0:12:57") == 3  # Three times that same formatted 777 seconds
