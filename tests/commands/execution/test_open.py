import webbrowser

from tests.commands.execution.utils import get_execution_data_mock
from tests.fixtures.data import EXECUTION_DETAIL_DATA
from tests.utils import make_call_stub
from valohai_cli.commands.execution.open import open


def test_open(monkeypatch, runner, logged_in_and_linked):
    call_stub = make_call_stub()
    monkeypatch.setattr(webbrowser, "open", call_stub)
    with get_execution_data_mock():
        runner.invoke(open, [str(EXECUTION_DETAIL_DATA["counter"])], catch_exceptions=False)
        assert call_stub.calls
