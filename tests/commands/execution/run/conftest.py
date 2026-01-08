import pytest

from tests.commands.run_test_utils import RunTestSetup
from tests.fixtures.config import CACHE_VOLUME_YAML, KUBE_RESOURCE_YAML


@pytest.fixture(params=["regular", "adhoc"], ids=("regular", "adhoc"))
def run_test_setup(request, logged_in_and_linked, monkeypatch):
    return RunTestSetup(monkeypatch=monkeypatch, adhoc=(request.param == "adhoc"))


@pytest.fixture(params=["regular", "adhoc"], ids=("regular", "adhoc"))
def run_test_setup_resources(request, logged_in_and_linked, monkeypatch):
    return RunTestSetup(
        monkeypatch=monkeypatch,
        adhoc=(request.param == "adhoc"),
        config_yaml=KUBE_RESOURCE_YAML,
    )


@pytest.fixture(params=["regular", "adhoc"], ids=("regular", "adhoc"))
def run_test_setup_cache_volumes(request, logged_in_and_linked, monkeypatch):
    return RunTestSetup(
        monkeypatch=monkeypatch,
        adhoc=(request.param == "adhoc"),
        config_yaml=CACHE_VOLUME_YAML,
    )
