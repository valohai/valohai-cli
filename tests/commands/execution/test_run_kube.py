import pytest

from tests.commands.run_test_utils import RunTestSetup
from tests.fixture_data import KUBE_RESOURCE_YAML


@pytest.fixture(params=["regular", "adhoc"], ids=("regular", "adhoc"))
def run_test_setup(request, logged_in_and_linked, monkeypatch):
    return RunTestSetup(monkeypatch=monkeypatch, adhoc=(request.param == "adhoc"))


@pytest.fixture(params=["regular", "adhoc"], ids=("regular", "adhoc"))
def run_test_setup_kube(request, logged_in_and_linked, monkeypatch):
    return RunTestSetup(
        monkeypatch=monkeypatch,
        adhoc=(request.param == "adhoc"),
        config_yaml=KUBE_RESOURCE_YAML,
    )


def test_kube_options(run_test_setup):
    run_test_setup.args.append("--k8s-cpu-min=1")
    run_test_setup.args.append("--k8s-memory-min=2")
    run_test_setup.args.append("--k8s-cpu-max=3")
    run_test_setup.args.append("--k8s-memory-max=4")
    run_test_setup.args.append("--k8s-device=nvidia.com/gpu=1")
    run_test_setup.run()

    assert run_test_setup.run_api_mock.last_create_execution_payload["runtime_config"] == {
        "kubernetes": {
            "containers": {
                "workload": {
                    "resources": {
                        "requests": {
                            "cpu": 1.0,
                            "memory": 2,
                        },
                        "limits": {
                            "cpu": 3,
                            "memory": 4,
                            "devices": {
                                "nvidia.com/gpu": 1,
                            },
                        },
                    },
                },
            },
        },
    }


def test_kube_options_partial(run_test_setup: RunTestSetup):
    run_test_setup.args.append("--k8s-cpu-min=1")
    run_test_setup.run()

    payload = run_test_setup.run_api_mock.last_create_execution_payload
    assert payload
    assert payload["runtime_config"] == {
        "kubernetes": {
            "containers": {
                "workload": {
                    "resources": {
                        "requests": {
                            "cpu": 1.0,
                        },
                    },
                },
            },
        },
    }


def test_kube_options_from_step(run_test_setup_kube: RunTestSetup):
    run_test_setup_kube.run()

    payload = run_test_setup_kube.run_api_mock.last_create_execution_payload
    assert payload
    assert payload["runtime_config"] == {
        "kubernetes": {
            "containers": {
                "workload": {
                    "resources": {
                        "requests": {
                            "cpu": 1.0,
                            "memory": 3,
                        },
                        "limits": {
                            "cpu": 2,
                            "memory": 4,
                            "devices": {
                                "nvidia.com/gpu": 1,
                            },
                        },
                    },
                },
            },
        },
    }


def test_kube_step_overrides(run_test_setup_kube: RunTestSetup):
    run_test_setup_kube.args.append("--k8s-cpu-min=1.5")
    run_test_setup_kube.args.append("--k8s-cpu-max=3")
    run_test_setup_kube.args.append("--k8s-device=amd.com/gpu=1")
    run_test_setup_kube.run()

    payload = run_test_setup_kube.run_api_mock.last_create_execution_payload
    assert payload
    assert payload["runtime_config"] == {
        "kubernetes": {
            "containers": {
                "workload": {
                    "resources": {
                        "requests": {
                            "cpu": 1.5,
                            "memory": 3,
                        },
                        "limits": {
                            "cpu": 3.0,
                            "memory": 4,
                            "devices": {
                                "amd.com/gpu": 1,
                            },
                        },
                    },
                },
            },
        },
    }


def test_kube_step_override_device_empty(run_test_setup_kube: RunTestSetup):
    run_test_setup_kube.args.append("--k8s-device-none")
    run_test_setup_kube.run()

    payload = run_test_setup_kube.run_api_mock.last_create_execution_payload
    assert payload
    assert payload["runtime_config"] == {
        "kubernetes": {
            "containers": {
                "workload": {
                    "resources": {
                        "requests": {
                            "cpu": 1.0,
                            "memory": 3,
                        },
                        "limits": {
                            "cpu": 2.0,
                            "memory": 4,
                            "devices": {},
                        },
                    },
                },
            },
        },
    }


def test_kube_runtime_config_preset_argument(run_test_setup_kube: RunTestSetup):
    preset_uuid = "yes-this-is-my-preset-uuid"
    run_test_setup_kube.args.append(f"--k8s-preset={preset_uuid}")
    run_test_setup_kube.run()

    payload = run_test_setup_kube.run_api_mock.last_create_execution_payload
    assert payload and payload["runtime_config_preset"] == preset_uuid


def test_kube_no_runtime_config_preset_argument(run_test_setup_kube: RunTestSetup):
    """Only add the preset to payload when explicitly specified."""
    run_test_setup_kube.run()
    payload = run_test_setup_kube.run_api_mock.last_create_execution_payload
    assert payload and "runtime_config_preset" not in payload
