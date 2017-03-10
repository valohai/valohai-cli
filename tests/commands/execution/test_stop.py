import requests_mock

from tests.fixture_data import EXECUTION_DATA
from valohai_cli.commands.execution.stop import stop


def test_stop_requires_arg(runner, logged_in_and_linked):
    output = runner.invoke(stop, catch_exceptions=False).output
    assert 'Nothing to stop' in output


def test_stop(runner, logged_in_and_linked):
    counter = EXECUTION_DATA['counter']

    with requests_mock.mock() as m:
        m.get('https://app.valohai.com/api/v0/executions/', json={
            'results': [EXECUTION_DATA],
        })
        m.post(EXECUTION_DATA['urls']['stop'], json={'message': 'OK'})

        output = runner.invoke(stop, ['#{}'.format(counter)], catch_exceptions=False).output
        assert 'Stopping #{}'.format(counter) in output
