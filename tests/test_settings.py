import os

import pytest
import requests_mock

from valohai_cli.api import request
from valohai_cli.settings import FilePersistence, get_settings_file_name, settings


@pytest.fixture
def temp_settings(monkeypatch, tmpdir):
    filename = str(tmpdir.join('settings.json'))
    monkeypatch.setattr(settings, 'persistence', FilePersistence(get_filename=lambda: filename))
    return settings


def test_settings_persistence(temp_settings):
    assert not settings.persistence.get('foo')
    settings.persistence.set('foo', 'bar')
    settings.persistence.update(baz='quux')
    settings.persistence.save()
    assert os.path.isfile(settings.persistence.get_filename())
    settings._data = None  # Pretend we don't have data
    assert settings.persistence.get('foo') == 'bar'
    assert settings.persistence.get('baz') == 'quux'


def test_get_settings_file_name():
    path = get_settings_file_name('.valohai-test.json')
    assert os.path.isdir(os.path.dirname(path))  # In a valid path
    assert path.endswith('.valohai-test.json')


@pytest.mark.parametrize("prefix", (None, 'Marvin/42.0.0'))
def test_user_agent(monkeypatch, logged_in, prefix):
    if prefix:
        monkeypatch.setattr(settings, 'api_user_agent_prefix', prefix)
    with requests_mock.mock() as m:
        m.get("http://192.168.1.1/", content=b'ok')
        request("GET", "http://192.168.1.1/")
        user_agent = m.last_request.headers["User-Agent"]
        assert 'valohai-cli' in user_agent
        if prefix:
            assert user_agent.startswith(prefix)
