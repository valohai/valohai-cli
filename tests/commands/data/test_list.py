import requests_mock

from tests.fixtures.data import DATUM_DATA
from valohai_cli.commands.data.list import list


def test_list(runner, logged_in_and_linked):
    with requests_mock.mock() as m:
        m.get(
            "https://app.valohai.com/api/v0/data/",
            json={
                "results": [
                    DATUM_DATA,
                    DATUM_DATA,
                    DATUM_DATA,
                ],
            },
        )

        output = runner.invoke(list, catch_exceptions=False).output
        assert output.count(f'datum://{DATUM_DATA["id"]}') == 3  # Three times the url
