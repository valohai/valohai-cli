import re

import requests_mock

from tests.fixture_data import (
    EVENT_RESPONSE_DATA, EXECUTION_DATA, OUTPUT_DATUM_DATA, OUTPUT_DATUM_DOWNLOAD_RESPONSE_DATA,
    OUTPUT_DATUM_RESPONSE_DATA, PROJECT_DATA
)

API_PREFIX = 'https://app.valohai.com/api/v0/'

def startswith(text):
    return re.compile('^' + re.escape(text))


def get_execution_data_mock():
    exec_id = EXECUTION_DATA['id']
    datum_id = OUTPUT_DATUM_DATA['id']
    m = requests_mock.mock()
    m.get(API_PREFIX + 'projects/{id}/'.format(id=PROJECT_DATA['id']), json=PROJECT_DATA)
    m.get(API_PREFIX + 'executions/', json={'results': [EXECUTION_DATA]})
    m.get(API_PREFIX + 'executions/{id}/'.format(id=exec_id), json=EXECUTION_DATA)
    m.get(API_PREFIX + 'executions/{id}/events/'.format(id=exec_id), json=EVENT_RESPONSE_DATA)
    m.get(API_PREFIX + 'data/?output_execution={id}&limit=9000'.format(id=exec_id), json=OUTPUT_DATUM_RESPONSE_DATA)
    m.get(API_PREFIX + 'data/{datum_id}/download/'.format(datum_id=datum_id), json=OUTPUT_DATUM_DOWNLOAD_RESPONSE_DATA)
    execution_by_counter_url = API_PREFIX + 'executions/{project_id}:{counter}/'.format(
        project_id=PROJECT_DATA['id'],
        counter=EXECUTION_DATA['counter'],
    )
    m.get(url=startswith(execution_by_counter_url), json=EXECUTION_DATA)
    m.delete(execution_by_counter_url, json={'ok': True})
    m.post(re.compile('^https://app.valohai.com/api/v0/data/(.+?)/purge/$'), json={'ok': True})
    return m
