import pytest

from valohai_cli.settings import settings
from valohai_cli.utils import get_project_directory

LOGGED_IN_DATA = {
    'host': 'https://app.valohai.com/',
    'user': {'id': 'x'},
    'token': 'x',
}

TEST_PROJECT_DATA = {
    "id": "000",
    "name": "nyan",
    "description": "nyan",
    "owner": 1,
    "ctime": "2016-12-16T12:25:52.718310Z",
    "mtime": "2017-01-20T14:35:02.196871Z",
}


@pytest.fixture
def logged_in(monkeypatch):
    monkeypatch.setattr(settings, '_data', LOGGED_IN_DATA)


@pytest.fixture
def logged_in_and_linked(monkeypatch):
    data = dict(
        LOGGED_IN_DATA,
        links={get_project_directory(): TEST_PROJECT_DATA}
    )

    monkeypatch.setattr(settings, '_data', data)
