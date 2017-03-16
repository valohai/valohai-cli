import requests_mock

from tests.fixture_data import PROJECT_DATA
from valohai_cli.commands.project.status import status


def test_status(runner, logged_in_and_linked):
    with requests_mock.mock() as m:
        project_data = dict(
            PROJECT_DATA,
            execution_summary={
                'count': 10,
            }
        )
        m.get('https://app.valohai.com/api/v0/projects/{id}/'.format(id=project_data['id']), json=project_data)
        m.get('https://app.valohai.com/api/v0/executions/', json={'results': []})
        runner.invoke(status, catch_exceptions=False)
        # TODO: Maybe check the output further?
