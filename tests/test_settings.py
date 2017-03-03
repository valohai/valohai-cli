import os

import pytest

from valohai_cli.settings import settings, get_settings_file_name


@pytest.fixture
def temp_settings(monkeypatch, tmpdir):
    filename = str(tmpdir.join('settings.json'))
    monkeypatch.setattr(settings, 'get_filename', lambda: filename)
    return settings


def test_settings(temp_settings):
    assert not settings.get('foo')
    settings['foo'] = 'bar'
    settings.update(baz='quux')
    settings.save()
    assert os.path.isfile(settings.get_filename())
    settings._data = None  # Pretend we don't have data
    assert settings['foo'] == 'bar'
    assert settings['baz'] == 'quux'



def test_get_settings_file_name():
    path = get_settings_file_name('.valohai-test.json')
    assert os.path.isdir(os.path.dirname(path))  # In a valid path
    assert path.endswith('.valohai-test.json')

