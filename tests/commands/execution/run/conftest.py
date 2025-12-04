import pytest

from tests.commands.run_test_utils import RunTestSetup


@pytest.fixture(params=["regular", "adhoc"], ids=("regular", "adhoc"))
def run_test_setup(request, logged_in_and_linked, monkeypatch):
    return RunTestSetup(monkeypatch=monkeypatch, adhoc=(request.param == "adhoc"))
