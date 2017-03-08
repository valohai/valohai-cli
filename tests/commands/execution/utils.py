import requests_mock

from tests.fixture_data import PROJECT_DATA, EXECUTION_DATA


def get_execution_data_mock():
    m = requests_mock.mock()
    m.get('https://app.valohai.com/api/v0/projects/{id}/'.format_map(PROJECT_DATA), json=PROJECT_DATA)
    m.get('https://app.valohai.com/api/v0/executions/', json={'results': [EXECUTION_DATA]})
    m.get('https://app.valohai.com/api/v0/executions/{id}/'.format_map(EXECUTION_DATA), json=EXECUTION_DATA)
    return m
