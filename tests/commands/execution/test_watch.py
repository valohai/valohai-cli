import time

from tests.commands.execution.utils import get_execution_data_mock, no_sleep
from tests.fixture_data import EXECUTION_DETAIL_DATA, PROJECT_DATA
from valohai_cli.commands.execution.watch import watch


def test_execution_watch(runner, logged_in_and_linked, monkeypatch):
    monkeypatch.setattr(time, "sleep", no_sleep)
    with get_execution_data_mock():
        output = runner.invoke(watch, [str(EXECUTION_DETAIL_DATA["counter"])], catch_exceptions=False).output
        assert EXECUTION_DETAIL_DATA["status"] in output
        assert PROJECT_DATA["name"] in output
        assert "hOI!!!" in output
        # TODO: Further test output?
