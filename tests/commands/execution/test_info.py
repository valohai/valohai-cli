from tests.commands.execution.utils import get_execution_data_mock
from tests.fixture_data import EXECUTION_DATA, PROJECT_DATA
from valohai_cli.commands.execution.info import info


def test_execution_info(runner, logged_in_and_linked):
    with get_execution_data_mock():
        output = runner.invoke(info, ['7'], catch_exceptions=False).output
        assert EXECUTION_DATA['status'] in output
        assert PROJECT_DATA['name'] in output
        assert EXECUTION_DATA['step'] in output
        assert all(p_name in output for p_name in EXECUTION_DATA['parameters'])
        # TODO: Further test output?
