from tests.commands.execution.utils import get_execution_data_mock
from tests.fixture_data import EXECUTION_DETAIL_DATA
from valohai_cli.commands.execution.summarize import summarize


def test_execution_summarize(runner, logged_in_and_linked):
    with get_execution_data_mock():
        output = runner.invoke(
            summarize,
            [str(EXECUTION_DETAIL_DATA["counter"])],
            catch_exceptions=False,
        ).output
        assert "777" in output
        assert "oispa" in output
        assert "beer" in output
        # TODO: test better?
