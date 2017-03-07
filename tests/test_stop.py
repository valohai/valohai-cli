import random

import requests_mock

from valohai_cli.commands.stop import stop


def test_stop(runner, logged_in_and_linked):
    counter = random.randint(10, 432222)
    stop_url = '/stahp/{0}{0}/'.format(counter)

    with requests_mock.mock() as m:
        m.get('https://app.valohai.com/api/v0/executions/', json={
            'results': [{'counter': counter, 'stop_url': stop_url}],
        })
        m.post('https://app.valohai.com{}'.format(stop_url), json={'message': 'OK'})

        output = runner.invoke(stop, ['#{}'.format(counter)], catch_exceptions=False).output
        assert 'Stopping #{}'.format(counter) in output
