def test_cache_volume_not_in_payload_when_unspecified_and_not_in_step(run_test_setup):
    run_test_setup.args.append("--k8s-cpu-min=1")
    run_test_setup.run()

    payload = run_test_setup.run_api_mock.last_create_execution_payload
    kubernetes_config = payload["runtime_config"]["kubernetes"]
    assert "cache_volumes" not in kubernetes_config


def test_cache_volume_and_none_mutually_exclusive(run_test_setup):
    run_test_setup.args.append("--k8s-cache-volume=my-cache")
    run_test_setup.args.append("--k8s-cache-volume-none")
    result = run_test_setup.run(catch_exceptions=True, verify_adhoc=False)

    assert "cannot be used together" in result


def test_cache_volume_parameter(run_test_setup):
    run_test_setup.args.append("--k8s-cache-volume=pvc-one")
    run_test_setup.args.append("--k8s-cache-volume=pvc-two")
    run_test_setup.run()

    payload = run_test_setup.run_api_mock.last_create_execution_payload
    assert payload["runtime_config"] == {
        "kubernetes": {
            "cache_volumes": [
                {"pvc_name": "pvc-one"},
                {"pvc_name": "pvc-two"},
            ],
        },
    }


def test_cache_volumes_with_resources(run_test_setup):
    run_test_setup.args.append("--k8s-cpu-min=1")
    run_test_setup.args.append("--k8s-cache-volume=my-cache")
    run_test_setup.run()

    payload = run_test_setup.run_api_mock.last_create_execution_payload
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
            "cache_volumes": [{"pvc_name": "my-cache"}],
        },
    }


def test_cache_volume_none(run_test_setup):
    run_test_setup.args.append("--k8s-cache-volume-none")
    run_test_setup.run()

    payload = run_test_setup.run_api_mock.last_create_execution_payload
    assert payload["runtime_config"] == {
        "kubernetes": {
            "cache_volumes": [],
        },
    }


def test_step_cache_volumes_used_when_no_cli_override(run_test_setup_cache_volumes):
    run_test_setup_cache_volumes.run()

    payload = run_test_setup_cache_volumes.run_api_mock.last_create_execution_payload
    assert payload["runtime_config"] == {
        "kubernetes": {
            "cache_volumes": [
                {"pvc_name": "default-cache-pvc"},
                {"pvc_name": "another-cache-pvc"},
            ],
        },
    }


def test_step_cache_volumes_overridden_by_cli(run_test_setup_cache_volumes):
    run_test_setup_cache_volumes.args.append("--k8s-cache-volume=cli-override-pvc")
    run_test_setup_cache_volumes.run()

    payload = run_test_setup_cache_volumes.run_api_mock.last_create_execution_payload
    assert payload["runtime_config"] == {
        "kubernetes": {
            "cache_volumes": [
                {"pvc_name": "cli-override-pvc"},
            ],
        },
    }


def test_step_cache_volumes_cleared_by_none_flag(run_test_setup_cache_volumes):
    run_test_setup_cache_volumes.args.append("--k8s-cache-volume-none")
    run_test_setup_cache_volumes.run()

    payload = run_test_setup_cache_volumes.run_api_mock.last_create_execution_payload
    assert payload["runtime_config"] == {
        "kubernetes": {
            "cache_volumes": [],
        },
    }
