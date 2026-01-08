import re
from re import Pattern

import requests_mock

from tests.fixtures.data import (
    EVENT_RESPONSE_DATA,
    EXECUTION_DETAIL_DATA,
    OUTPUT_DATUM_DATA,
    OUTPUT_DATUM_DOWNLOAD_RESPONSE_DATA,
    OUTPUT_DATUM_RESPONSE_DATA,
    PROJECT_DATA,
)

API_PREFIX = "https://app.valohai.com/api/v0/"


def get_startswith_re(text: str) -> Pattern:
    return re.compile(f"^{re.escape(text)}")


def get_execution_data_mock():
    exec_id = EXECUTION_DETAIL_DATA["id"]
    datum_id = OUTPUT_DATUM_DATA["id"]
    m = requests_mock.mock()
    project_id = PROJECT_DATA["id"]
    execution_counter = EXECUTION_DETAIL_DATA["counter"]
    m.get(f"{API_PREFIX}projects/{project_id}/", json=PROJECT_DATA)
    m.get(f"{API_PREFIX}executions/", json={"results": [EXECUTION_DETAIL_DATA]})  # This should use list data
    m.get(f"{API_PREFIX}executions/{exec_id}/", json=EXECUTION_DETAIL_DATA)
    m.get(f"{API_PREFIX}executions/{exec_id}/events/", json=EVENT_RESPONSE_DATA)
    m.get(f"{API_PREFIX}data/?output_execution={exec_id}&limit=5000", json=OUTPUT_DATUM_RESPONSE_DATA)
    m.get(f"{API_PREFIX}data/{datum_id}/download/", json=OUTPUT_DATUM_DOWNLOAD_RESPONSE_DATA)
    execution_by_counter_url = f"{API_PREFIX}executions/{project_id}:{execution_counter}/"
    m.get(url=get_startswith_re(execution_by_counter_url), json=EXECUTION_DETAIL_DATA)
    m.delete(execution_by_counter_url, json={"ok": True})
    m.post(re.compile("^https://app.valohai.com/api/v0/data/(.+?)/purge/$"), json={"ok": True})
    return m


def no_sleep(t):
    raise KeyboardInterrupt("no... sleep... til... Brooklyn!")
