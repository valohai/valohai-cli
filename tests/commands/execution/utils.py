import requests_mock

from tests.fixture_data import EXECUTION_DATA, PROJECT_DATA, EVENT_RESPONSE_DATA


def get_execution_data_mock():
    m = requests_mock.mock()
    m.get('https://app.valohai.com/api/v0/projects/{id}/'.format(id=PROJECT_DATA['id']), json=PROJECT_DATA)
    m.get('https://app.valohai.com/api/v0/executions/', json={'results': [EXECUTION_DATA]})
    m.get('https://app.valohai.com/api/v0/executions/{id}/'.format(id=EXECUTION_DATA['id']), json=EXECUTION_DATA)
    m.get('https://app.valohai.com/api/v0/executions/{id}/events/'.format(id=EXECUTION_DATA['id']), json=EVENT_RESPONSE_DATA)
    return m
