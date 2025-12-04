from tests.commands.run_test_utils import RunTestSetup


def test_kube_runtime_config_preset_argument(run_test_setup_resources: RunTestSetup):
    preset_uuid = "yes-this-is-my-preset-uuid"
    run_test_setup_resources.args.append(f"--k8s-preset={preset_uuid}")
    run_test_setup_resources.run()

    payload = run_test_setup_resources.run_api_mock.last_create_execution_payload
    assert payload and payload["runtime_config_preset"] == preset_uuid


def test_kube_no_runtime_config_preset_argument(run_test_setup_resources: RunTestSetup):
    """Only add the preset to payload when explicitly specified."""
    run_test_setup_resources.run()
    payload = run_test_setup_resources.run_api_mock.last_create_execution_payload
    assert payload and "runtime_config_preset" not in payload
