import webbrowser

import requests_mock

from tests.fixtures.data import PROJECT_DATA
from tests.utils import make_call_stub
from valohai_cli.commands.project.open import open


def test_open(monkeypatch, runner, logged_in_and_linked):
    call_stub = make_call_stub()
    monkeypatch.setattr(webbrowser, "open", call_stub)
    with requests_mock.mock() as m:
        project_data = dict(PROJECT_DATA)
        m.get(f"https://app.valohai.com/api/v0/projects/{project_data['id']}/", json=project_data)
        runner.invoke(open, catch_exceptions=False)
        assert call_stub.calls
