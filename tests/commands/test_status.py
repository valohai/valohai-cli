import requests_mock

from tests.conftest import TEST_PROJECT_DATA
from valohai_cli.commands.status import status


def test_status(runner, logged_in_and_linked):
    with requests_mock.mock() as m:
        project_data = dict(
            TEST_PROJECT_DATA,
            execution_summary={
                'count': 10,
            }
        )
        m.get('https://app.valohai.com/api/v0/projects/{id}/'.format_map(project_data), json=project_data)
        m.get('https://app.valohai.com/api/v0/executions/', json={'results': []})
        runner.invoke(status, catch_exceptions=False)
        # TODO: Maybe check the output further?
