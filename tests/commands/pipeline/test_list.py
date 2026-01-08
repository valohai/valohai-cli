import requests_mock

from tests.fixtures.data import PIPELINE_DATA
from valohai_cli.commands.pipeline.list import list


def test_list(runner, logged_in_and_linked):
    with requests_mock.mock() as m:
        m.get(
            "https://app.valohai.com/api/v0/pipelines/",
            json={
                "results": [
                    PIPELINE_DATA,
                    PIPELINE_DATA,
                    PIPELINE_DATA,
                ],
            },
        )

        output = runner.invoke(list, catch_exceptions=False).output
        assert "Training Pipeline" in output
        assert output.count("started") == 3
