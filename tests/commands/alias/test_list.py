import requests_mock

from tests.fixture_data import DATUM_ALIAS_DATA
from valohai_cli.commands.alias.list import list


def test_list(runner, logged_in_and_linked):
    with requests_mock.mock() as m:
        m.get(
            "https://app.valohai.com/api/v0/datum-aliases/",
            json={
                "results": [
                    DATUM_ALIAS_DATA,
                    DATUM_ALIAS_DATA,
                    DATUM_ALIAS_DATA,
                ],
            },
        )

        output = runner.invoke(list, catch_exceptions=False).output
        assert output.count("datum://this-is-alias-for-latest-png") == 3  # Three times the url
