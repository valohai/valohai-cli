import requests_mock

from tests.fixtures.data import TASK_LIST_DATA
from valohai_cli.commands.task.list import list


def test_list(runner, logged_in_and_linked):
    with requests_mock.mock() as m:
        m.get(
            "https://app.valohai.com/api/v0/tasks/",
            json={
                "results": [
                    TASK_LIST_DATA,
                    TASK_LIST_DATA,
                    TASK_LIST_DATA,
                ],
            },
        )

        output = runner.invoke(list, catch_exceptions=False).output
        assert "Training Task" in output
        assert output.count("started") == 3
