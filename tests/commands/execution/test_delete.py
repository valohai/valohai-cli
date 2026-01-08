from tests.commands.execution.utils import get_execution_data_mock
from tests.fixtures.data import EXECUTION_DETAIL_DATA
from valohai_cli.commands.execution.delete import delete


def test_execution_delete(runner, logged_in_and_linked):
    with get_execution_data_mock():
        output = runner.invoke(
            delete,
            ["--purge-outputs", str(EXECUTION_DETAIL_DATA["counter"])],
            catch_exceptions=False,
        ).output
        assert "Deleted 1" in output
        # TODO: test better?
