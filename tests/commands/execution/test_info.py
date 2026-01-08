from tests.commands.execution.utils import get_execution_data_mock
from tests.fixtures.data import EXECUTION_DETAIL_DATA, PROJECT_DATA
from valohai_cli.commands.execution.info import info


def test_execution_info(runner, logged_in_and_linked):
    with get_execution_data_mock():
        output = runner.invoke(info, [str(EXECUTION_DETAIL_DATA["counter"])], catch_exceptions=False).output
        assert EXECUTION_DETAIL_DATA["status"] in output
        assert PROJECT_DATA["name"] in output
        assert EXECUTION_DETAIL_DATA["step"] in output
        assert all(p_name in output for p_name in EXECUTION_DETAIL_DATA["parameters"])
        # TODO: Further test output?
