from tests.commands.run_test_utils import RunTestSetup


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


def test_kube_options_from_step(run_test_setup_resources: RunTestSetup):
    run_test_setup_resources.run()

    payload = run_test_setup_resources.run_api_mock.last_create_execution_payload
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


def test_kube_step_overrides(run_test_setup_resources: RunTestSetup):
    run_test_setup_resources.args.append("--k8s-cpu-min=1.5")
    run_test_setup_resources.args.append("--k8s-cpu-max=3")
    run_test_setup_resources.args.append("--k8s-device=amd.com/gpu=1")
    run_test_setup_resources.run()

    payload = run_test_setup_resources.run_api_mock.last_create_execution_payload
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


def test_kube_step_override_device_empty(run_test_setup_resources: RunTestSetup):
    run_test_setup_resources.args.append("--k8s-device-none")
    run_test_setup_resources.run()

    payload = run_test_setup_resources.run_api_mock.last_create_execution_payload
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
