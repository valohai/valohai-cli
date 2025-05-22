from tests.fixture_data import NOTEBOOK_EXECUTION_DATA
from valohai_cli.commands.notebook.run import run


def test_run_success(runner, logged_in_and_linked, using_default_run_api_mock):
    args = ("--environment", "env-slug", "--image", "python:3.14")
    counter = NOTEBOOK_EXECUTION_DATA["counter"]

    output = runner.invoke(run, args).output

    assert "Success" in output
    assert f"Notebook execution {counter} queued" in output
