from tests.commands.execution.utils import get_execution_data_mock
from tests.fixture_data import EXECUTION_DATA
from valohai_cli.commands.execution.logs import logs


def test_logs(runner, logged_in_and_linked):
    counter = EXECUTION_DATA["counter"]

    with get_execution_data_mock():
        output = runner.invoke(logs, [str(counter)], catch_exceptions=False).output
        assert "temmie" in output and "oh no" in output
        output = runner.invoke(logs, ["--no-stderr", str(counter)], catch_exceptions=False).output
        assert "temmie" in output and "oh no" not in output
