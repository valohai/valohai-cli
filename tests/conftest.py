import pytest

from tests.fixture_data import LOGGED_IN_DATA, PROJECT_DATA
from valohai_cli.settings import settings
from valohai_cli.utils import get_project_directory


@pytest.fixture
def logged_in(monkeypatch):
    monkeypatch.setattr(settings, '_data', LOGGED_IN_DATA)


@pytest.fixture
def logged_in_and_linked(monkeypatch):
    data = dict(
        LOGGED_IN_DATA,
        links={get_project_directory(): PROJECT_DATA}
    )

    monkeypatch.setattr(settings, '_data', data)
