import pytest

from tests.fixture_data import NOTEBOOK_EXECUTION_DATA
from valohai_cli.commands.notebook.run import run


@pytest.mark.parametrize("with_envvars", [True, False])
def test_run_success(runner, logged_in_and_linked, using_default_run_api_mock, with_envvars: bool):
    args = ["--environment", "env-slug", "--image", "python:3.14"]
    if with_envvars:
        args.extend(["--var", "FOO=bar", "--var", "BAZ=qux"])
    res = runner.invoke(run, args)
    assert res.exit_code == 0
    counter = NOTEBOOK_EXECUTION_DATA["counter"]
    assert "Success" in res.output
    assert f"Notebook execution {counter} queued" in res.output
    payload = using_default_run_api_mock.last_create_notebook_execution_payload
    assert payload["environment"] == "env-slug"
    assert payload["image"] == "python:3.14"
    if with_envvars:
        assert payload["environment_variables"] == {"FOO": "bar", "BAZ": "qux"}
