import os
import subprocess

import pytest
import yaml

from tests.commands.run_test_utils import ALTERNATIVE_YAML, RunAPIMock, RunTestSetup
from tests.fixture_data import CONFIG_YAML, KUBE_RESOURCE_YAML, PROJECT_DATA
from valohai_cli.commands.execution.run import run
from valohai_cli.ctx import get_project
from valohai_cli.models.project import Project

adhoc_mark = pytest.mark.parametrize("adhoc", (False, True), ids=("regular", "adhoc"))


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


@pytest.fixture()
def patch_git(monkeypatch):
    def mock_resolve_commits(mock_self, *, commit_identifier):
        return [{"identifier": commit_identifier}]

    monkeypatch.setattr(Project, "resolve_commits", mock_resolve_commits)


def test_run_requires_step(runner, logged_in_and_linked):
    assert "Usage: run" in runner.invoke(run, catch_exceptions=False).output


@pytest.mark.parametrize("pass_env_var", ("custom", "override-default"))
def test_run_env_var(run_test_setup, pass_env_var):
    run_test_setup.args.extend(["-v", "greeting=hello"])
    run_test_setup.args.extend(["--var", "enable=1"])
    run_test_setup.args.extend(["-vdebug=yes"])
    if pass_env_var == "override-default":
        run_test_setup.args.extend(["--var", "testenvvar="])
        expected_testenvvar = ""
    else:
        expected_testenvvar = "test"  # default from YAML
    run_test_setup.values["environment_variables"] = {
        "greeting": "hello",
        "enable": "1",
        "debug": "yes",
        "testenvvar": expected_testenvvar,
    }
    run_test_setup.run()


def test_run_env(run_test_setup):
    run_test_setup.args.append("--environment=015dbd56-2670-b03e-f37c-dc342714f1b5")
    run_test_setup.values["environment"] = "015dbd56-2670-b03e-f37c-dc342714f1b5"
    run_test_setup.run()


def test_run_tags(run_test_setup):
    run_test_setup.args.extend(["--tag=bark", "--tag=bork", "--tag=vuh", "--tag=hau"])
    run_test_setup.values["tags"] = ["bark", "bork", "vuh", "hau"]
    run_test_setup.run()


def test_run_spot_restart(run_test_setup):
    run_test_setup.args.append("--environment=018161d4-2911-7bbb-85ea-8820559cce89")
    run_test_setup.values["environment"] = "018161d4-2911-7bbb-85ea-8820559cce89"
    run_test_setup.args.append("--autorestart")
    run_test_setup.run()
    assert run_test_setup.run_api_mock.last_create_execution_payload["runtime_config"] == {
        "autorestart": True,
    }


@pytest.mark.parametrize("time_limit", (None, 121, 0, "10min"))
def test_run_time_limit(run_test_setup, time_limit):
    """Make sure that the time-limit setting is correctly passed from YAML config to the API."""
    step_config = """
- step:
    name: Train model
    image: busybox
    command: "false"
"""
    if time_limit is not None:
        step_config += f"    time-limit: {time_limit}\n"

    with open(get_project().get_config_filename(), "w") as yaml_fp:
        yaml_fp.write(step_config)

    run_test_setup.run()
    if time_limit:
        time_limit_in_seconds = 600 if time_limit == "10min" else time_limit
        assert (
            run_test_setup.run_api_mock.last_create_execution_payload["time_limit"] == time_limit_in_seconds
        )
    else:
        assert "time_limit" not in run_test_setup.run_api_mock.last_create_execution_payload


def test_run_with_yaml_path(run_test_setup):
    run_test_setup.args.remove("train")
    # Use a step which is only present in the evaluation YAML
    run_test_setup.args.append("batch feature extraction")
    run_test_setup.args.append(f"--yaml={ALTERNATIVE_YAML}")
    output = run_test_setup.run(verify_adhoc=run_test_setup.adhoc)
    # Adhoc success case already verified in `run()
    if not run_test_setup.adhoc:
        assert "--yaml can only be used with --adhoc" in output
    else:
        assert f"from configuration YAML at {ALTERNATIVE_YAML}" in output


def test_run_input(run_test_setup):
    run_test_setup.args.append("--in1=http://url")
    run_test_setup.args.append("--in1=http://anotherurl")
    run_test_setup.values["inputs"] = {"in1": ["http://url", "http://anotherurl"]}
    run_test_setup.run()


@pytest.mark.parametrize("pass_param", ("direct", "file", "mix"))
def test_run_params(tmpdir, run_test_setup, pass_param):
    values = {
        "parameters": {  # default from YAML
            "max_steps": 300,
            "learning_rate": 0.1337,
        },
    }
    if pass_param in ("direct", "mix"):
        run_test_setup.args.append("--max-steps=1801")
        values["parameters"]["max_steps"] = 1801

    if pass_param in ("file", "mix"):
        params_yaml = tmpdir.join("params.yaml")
        params_yaml.write(yaml.safe_dump({"learning-rate": 1700}))
        run_test_setup.args.append(f"--parameter-file={params_yaml}")
        values["parameters"]["learning_rate"] = 1700
    run_test_setup.values.update(values)
    run_test_setup.run()
    payload = run_test_setup.run_api_mock.last_create_execution_payload
    if pass_param == "direct":
        assert payload["parameters"]["max_steps"] == 1801
        assert payload["parameters"]["learning_rate"] == 0.1337
    if pass_param == "file":
        assert payload["parameters"]["max_steps"] == 300
        assert payload["parameters"]["learning_rate"] == 1700.0
    if pass_param == "mix":
        assert payload["parameters"]["max_steps"] == 1801
        assert payload["parameters"]["learning_rate"] == 1700.0


def test_param_type_validation_integer(runner, logged_in_and_linked, patch_git, default_run_api_mock):
    with open(get_project().get_config_filename(), "w") as yaml_fp:
        yaml_fp.write(CONFIG_YAML)
    rv = runner.invoke(run, ["train", "--max-steps=plonk"], catch_exceptions=False)
    assert "'plonk' is not a valid integer" in rv.output or "plonk is not a valid integer" in rv.output


def test_param_type_validation_flag(runner, logged_in_and_linked, patch_git, default_run_api_mock):
    with open(get_project().get_config_filename(), "w") as yaml_fp:
        yaml_fp.write(CONFIG_YAML)
    rv = runner.invoke(run, ["train", "--enable-mega-boost=please"], catch_exceptions=False)
    assert "'please' is not a valid boolean" in rv.output or "please is not a valid boolean" in rv.output


@pytest.mark.parametrize(
    "value, result",
    [
        # Various forms supported by `click.BOOL`...
        ("yes", True),
        ("no", False),
        ("1", True),
        ("FALSE", False),
        ("True", True),
    ],
)
def test_flag_param_coercion(tmpdir, run_test_setup, value, result):
    run_test_setup.values["parameters"] = {  # default from YAML
        "max_steps": 300,
        "learning_rate": 0.1337,
        "enable_mega_boost": result,
    }
    run_test_setup.args.append(f"--enable-mega-boost={value}")
    run_test_setup.run()


def test_run_no_git(runner, logged_in_and_linked):
    project_id = PROJECT_DATA["id"]

    with open(get_project().get_config_filename(), "w") as yaml_fp:
        yaml_fp.write(CONFIG_YAML)

    args = ["train"]

    with RunAPIMock(project_id, "f" * 16, {}):
        output = runner.invoke(run, args, catch_exceptions=False).output
        assert "is not a Git repository" in output


def test_param_input_sanitization(runner, logged_in_and_linked, patch_git, default_run_api_mock):
    with open(get_project().get_config_filename(), "w") as yaml_fp:
        yaml_fp.write("""
- step:
    name: Train model
    image: busybox
    command: "false"
    inputs:
      - name: Ridiculously Complex Input_Name
        default: http://example.com/
    parameters:
      - name: Parameter With Highly Convoluted Name
        pass-as: --simple={v}
        type: integer
        default: 1
""")
    output = runner.invoke(run, ["train", "--help"], catch_exceptions=False).output
    assert "--Parameter-With-Highly-Convoluted-Name" in output
    assert "--parameter-with-highly-convoluted-name" in output
    assert "--Ridiculously-Complex-Input-Name" in output
    assert "--ridiculously-complex-input-name" in output


def test_multi_parameter_serialization(run_test_setup):
    run_test_setup.run()
    payload = run_test_setup.run_api_mock.last_create_execution_payload
    assert payload["parameters"]["multi-parameter"] == ["one", "two", "three"]


def test_multi_parameter_command_line_argument(run_test_setup):
    run_test_setup.args.append("--multi-parameter=four")
    run_test_setup.args.append("--multi-parameter=5")
    run_test_setup.args.append('--multi-parameter="six"')
    run_test_setup.run()
    payload = run_test_setup.run_api_mock.last_create_execution_payload

    assert payload["parameters"]["multi-parameter"] == ["four", "5", '"six"']


def test_typo_check(runner, logged_in_and_linked, patch_git, default_run_api_mock):
    with open(get_project().get_config_filename(), "w") as yaml_fp:
        yaml_fp.write(CONFIG_YAML)
    args = ["train", "--max-setps=80"]  # Oopsy!
    output = runner.invoke(run, args, catch_exceptions=False).output
    assert "(Possible options:" in output or "Did you mean" in output
    assert "--max-steps" in output


def test_run_help(runner, logged_in_and_linked):
    with open(get_project().get_config_filename(), "w") as yaml_fp:
        yaml_fp.write(CONFIG_YAML)

    output = runner.invoke(run, ["--help"], catch_exceptions=False).output
    assert "Train model" in output


def test_command_help(runner, logged_in_and_linked, patch_git, default_run_api_mock):
    with open(get_project().get_config_filename(), "w") as yaml_fp:
        yaml_fp.write(CONFIG_YAML)

    output = runner.invoke(run, ["Train model", "--help"], catch_exceptions=False).output
    assert "Parameter Options" in output
    assert "Input Options" in output


def test_remote(run_test_setup, tmpdir):
    key = tmpdir.join("key.pub")
    key.write_text("ssh blarp blep", "utf-8")
    run_test_setup.args.append("--debug-port=8101")
    run_test_setup.args.append(f"--debug-key-file={key}")
    run_test_setup.run()
    assert run_test_setup.run_api_mock.last_create_execution_payload["runtime_config"] == {
        "remote_debug": {
            "debug_key": "ssh blarp blep",
            "debug_port": 8101,
        },
    }


def test_remote_both_args(run_test_setup):
    run_test_setup.args.append("--debug-port=8101")
    assert "Both or neither" in run_test_setup.run(catch_exceptions=False, verify_adhoc=False)


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


def test_kube_options_partial(run_test_setup):
    run_test_setup.args.append("--k8s-cpu-min=1")
    run_test_setup.run()

    assert run_test_setup.run_api_mock.last_create_execution_payload["runtime_config"] == {
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


def test_kube_options_from_step(run_test_setup_kube):
    run_test_setup_kube.run()

    assert run_test_setup_kube.run_api_mock.last_create_execution_payload["runtime_config"] == {
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


def test_kube_step_overrides(run_test_setup_kube):
    run_test_setup_kube.args.append("--k8s-cpu-min=1.5")
    run_test_setup_kube.args.append("--k8s-cpu-max=3")
    run_test_setup_kube.args.append("--k8s-device=amd.com/gpu=1")
    run_test_setup_kube.run()

    assert run_test_setup_kube.run_api_mock.last_create_execution_payload["runtime_config"] == {
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


def test_kube_step_override_device_empty(run_test_setup_kube):
    run_test_setup_kube.args.append("--k8s-device-none")
    run_test_setup_kube.run()

    assert run_test_setup_kube.run_api_mock.last_create_execution_payload["runtime_config"] == {
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


def test_kube_runtime_config_preset_argument(run_test_setup_kube):
    preset_uuid = "yes-this-is-my-preset-uuid"
    run_test_setup_kube.args.append(f"--k8s-preset={preset_uuid}")
    run_test_setup_kube.run()

    assert (
        run_test_setup_kube.run_api_mock.last_create_execution_payload["runtime_config_preset"] == preset_uuid
    )


def test_kube_no_runtime_config_preset_argument(run_test_setup_kube):
    """Only add the preset to payload when explicitly specified."""
    run_test_setup_kube.run()

    assert "runtime_config_preset" not in run_test_setup_kube.run_api_mock.last_create_execution_payload


@pytest.mark.parametrize("allow_git_packaging", (True, False))
def test_no_git_adhoc_packaging(logged_in_and_linked, monkeypatch, allow_git_packaging):
    proj_dir = os.environ["VALOHAI_PROJECT_DIR"]  # set by `isolate_cli` autouse fixture
    rts = RunTestSetup(monkeypatch=monkeypatch, adhoc=True)
    try:
        subprocess.check_call("git init -b x", cwd=proj_dir, shell=True)
        subprocess.check_call("git add .", cwd=proj_dir, shell=True)
        subprocess.check_call("git commit -q -m x", cwd=proj_dir, shell=True)
    except subprocess.CalledProcessError as e:
        pytest.skip(f"Failed to set up git repository: {e}")
    if not allow_git_packaging:
        rts.args.append("--no-git-packaging")
    output = rts.run()
    if allow_git_packaging:
        assert "Used git to find" in output
    else:
        assert "Walked filesystem and found" in output


@pytest.mark.parametrize("val", (0, 7, 42))
def test_priority(run_test_setup, val):
    run_test_setup.args.append(f"--priority={val}")
    run_test_setup.run()
    assert run_test_setup.run_api_mock.last_create_execution_payload["priority"] == val


def test_implicit_priority(run_test_setup):
    run_test_setup.args.append("--priority")
    run_test_setup.run()
    assert run_test_setup.run_api_mock.last_create_execution_payload["priority"] == 1
