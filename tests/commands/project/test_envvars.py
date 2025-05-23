import pytest
import requests_mock

from tests.fixture_data import PROJECT_DATA
from valohai_cli.commands.project.environment_variables.create import create
from valohai_cli.commands.project.environment_variables.delete import delete
from valohai_cli.commands.project.environment_variables.list import list


def test_list_envvars(runner, logged_in_and_linked):
    with requests_mock.mock() as m:
        m.get(f"https://app.valohai.com/api/v0/projects/{PROJECT_DATA['id']}/", json=PROJECT_DATA)
        result = runner.invoke(list)
    for key, ev in PROJECT_DATA["environment_variables"].items():
        assert key in result.output
        assert (ev["value"] if not ev["secret"] else "****") in result.output


def test_create_envvar(runner, logged_in_and_linked):
    with requests_mock.mock() as m:
        m.post(
            f"https://app.valohai.com/api/v0/projects/{PROJECT_DATA['id']}/environment_variable/",
            json={},
        )
        result = runner.invoke(create, ["--secret", "hey=ho=lets=go", "eeuu=oouuuhhh"])
        assert result.exit_code == 0
        assert [r.json() for r in m.request_history] == [
            {"name": "hey", "secret": True, "value": "ho=lets=go"},
            {"name": "eeuu", "secret": True, "value": "oouuuhhh"},
        ]


@pytest.mark.parametrize(
    "args",
    [
        "foo",
        "^38=fbar",
        "3aa=kdkd",
    ],
)
def test_create_envvar_bad(runner, logged_in_and_linked, args):
    result = runner.invoke(create, args)
    assert result.exit_code != 0


def test_delete_envvar(runner, logged_in_and_linked):
    with requests_mock.mock() as m:
        m.delete(
            f"https://app.valohai.com/api/v0/projects/{PROJECT_DATA['id']}/environment_variable/",
            json={},
        )
        result = runner.invoke(delete, ["hey"])
        assert result.exit_code == 0
        assert [r.json() for r in m.request_history] == [
            {"name": "hey"},
        ]
