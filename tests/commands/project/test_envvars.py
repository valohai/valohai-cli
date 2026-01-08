from contextlib import contextmanager

import pytest
import requests_mock

from tests.fixtures.data import PROJECT_DATA
from valohai_cli.commands.project.environment_variables.create import create
from valohai_cli.commands.project.environment_variables.delete import delete
from valohai_cli.commands.project.environment_variables.list import list


@contextmanager
def env_var_api_mock():
    with requests_mock.mock() as m:
        project_url = f"https://app.valohai.com/api/v0/projects/{PROJECT_DATA['id']}/"
        m.get(project_url, json=PROJECT_DATA)
        m.post(f"{project_url}environment_variable/", json={})
        m.delete(f"{project_url}environment_variable/", json={})
        yield m


def test_list_envvars(runner, logged_in_and_linked):
    with env_var_api_mock():
        result = runner.invoke(list)
    for key, ev in PROJECT_DATA["environment_variables"].items():
        assert key in result.output
        assert (ev["value"] if not ev["secret"] else "****") in result.output


def test_create_envvar_secret(runner, logged_in_and_linked):
    with env_var_api_mock() as m:
        result = runner.invoke(create, ["--secret", "hey=ho=lets=go", "eeuu=oouuuhhh"])
        assert result.exit_code == 0
        assert [r.json() for r in m.request_history] == [
            {"name": "hey", "secret": True, "value": "ho=lets=go"},
            {"name": "eeuu", "secret": True, "value": "oouuuhhh"},
        ]


def test_create_envvar_nonsecret(runner, logged_in_and_linked):
    with env_var_api_mock() as m:
        result = runner.invoke(create, ["BANANA_HAMMOCK_ENABLED=true"])
        print(result.output)
        assert result.exit_code == 0
        assert [r.json() for r in m.request_history] == [
            {"name": "BANANA_HAMMOCK_ENABLED", "secret": False, "value": "true"},
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
    with env_var_api_mock() as m:
        result = runner.invoke(delete, ["hey"])
        assert result.exit_code == 0
        assert [r.json() for r in m.request_history] == [
            {"name": "hey"},
        ]
