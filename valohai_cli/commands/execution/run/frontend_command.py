from __future__ import annotations

import contextlib
from typing import Any

import click

from valohai_cli.ctx import get_project
from valohai_cli.messages import info
from valohai_cli.utils import parse_environment_variable_strings
from valohai_cli.utils.commits import create_or_resolve_commit

from .dynamic_run_command import RunCommand
from .utils import match_step

run_epilog = (
    "More detailed help (e.g. how to define parameters and inputs) is available when you have "
    "defined which step to run. For instance, if you have a step called Extract, "
    'try running "vh exec run Extract --help". (This is denoted by STEP-OPTIONS... in the usage.)'
)


EMPTY_DICT_PLACEHOLDER = object()


@click.command(
    context_settings={"ignore_unknown_options": True},
    add_help_option=False,
    epilog=run_epilog,
)
@click.argument("step_name", required=False, metavar="STEP-NAME")
@click.option(
    "--commit",
    "-c",
    default=None,
    metavar="SHA",
    help="The commit to use. Defaults to the current HEAD.",
)
@click.option(
    "--environment",
    "-e",
    default=None,
    help='The environment UUID or slug to use (see "vh environments")',
)
@click.option(
    "--environment-variable-groups",
    "environment_variable_groups",
    multiple=True,
    default=None,
    help="Add environment variable group UUIDs.",
)
@click.option(
    "--image",
    "-i",
    default=None,
    help="Override the Docker image specified in the step.",
)
@click.option(
    "--title",
    "-t",
    default=None,
    help="Title of the execution.",
)
@click.option(
    "--watch",
    "-w",
    is_flag=True,
    help='Start "exec watch"ing the execution after it starts.',
)
@click.option(
    "--open-browser",
    is_flag=True,
    help="Open default web browser to execution page after it starts.",
)
@click.option(
    "--var",
    "-v",
    "environment_variables",
    multiple=True,
    help="Add environment variable (NAME=VALUE). May be repeated.",
)
@click.option(
    "--tag",
    "tags",
    multiple=True,
    help="Tag the execution. May be repeated.",
)
@click.option(
    "--sync",
    "-s",
    "download_directory",
    type=click.Path(file_okay=False),
    help="Download execution outputs to DIRECTORY.",
    default=None,
)
@click.option(
    "--adhoc",
    "-a",
    is_flag=True,
    help="Upload the current state of the working directory, then run it as an ad-hoc execution.",
)
@click.option(
    "--git-packaging/--no-git-packaging",
    "-g/-G",
    default=True,
    is_flag=True,
    help="When creating ad-hoc tasks, whether to allow using Git for packaging directory contents.",
)
@click.option(
    "--validate-adhoc/--no-validate-adhoc",
    help="Enable or disable validation of adhoc packaged code, on by default",
    default=True,
)
@click.option(
    "--yaml",
    default=None,
    help="The path to the configuration YAML (valohai.yaml) file to use.",
)
@click.option(
    "--debug-port",
    type=int,
    help="Configure the port for remote debugging the execution via SSH after it starts.",
)
@click.option(
    "--debug-key-file",
    type=click.Path(file_okay=True, readable=True, writable=False),
    help="Path to a public SSH key file for remote debugging the execution after it starts.",
)
@click.option(
    "--ssh",
    is_flag=True,
    help="Start ssh remote connection for debugging the execution after it starts.",
)
@click.option(
    "--autorestart/--no-autorestart",
    help="Enable Automatic Restart on Spot Instance Interruption",
)
@click.option(
    "--priority",
    type=int,
    default=None,
    is_flag=False,
    flag_value=1,
    help="Priority for the job; higher values mean higher priority.",
)
@click.option(
    "--k8s-cpu-min",
    help="Kubernetes only. CPU resource request",
    type=float,
)
@click.option(
    "--k8s-memory-min",
    help="Kubernetes only. Memory resource request. Unit is binary megabytes (Mi)",
    type=int,
)
@click.option(
    "--k8s-cpu-max",
    help="Kubernetes only. CPU resource request",
    type=float,
)
@click.option(
    "--k8s-memory-max",
    help="Kubernetes only. Memory resource request. Unit is binary megabytes (Mi)",
    type=int,
)
@click.option(
    "--k8s-device",
    "k8s_devices",
    multiple=True,
    help="Kubernetes only. Custom device claim. Format: NAME=VALUE. May be repeated for multiple limits.",
)
@click.option(
    "--k8s-device-none",
    is_flag=True,
    help="Kubernetes only. Request no device claims, not even if there is a default",
)
@click.option(
    "--k8s-preset",
    default=None,
    help="Kubernetes only. Custom runtime config preset UUID",
)
@click.argument(
    "args",
    nargs=-1,
    type=click.UNPROCESSED,
    metavar="STEP-OPTIONS...",
)
@click.pass_context
def run(
    ctx: click.Context,
    *,
    adhoc: bool,
    git_packaging: bool = True,
    args: list[str],
    commit: str | None,
    yaml: str | None,
    download_directory: str | None,
    environment: str | None,
    environment_variables: list[str],
    environment_variable_groups: list[str] | None,
    image: str | None,
    step_name: str | None,
    tags: list[str],
    title: str | None,
    validate_adhoc: bool,
    watch: bool,
    open_browser: bool,
    debug_port: int,
    debug_key_file: str | None,
    autorestart: bool,
    priority: int | None,
    k8s_cpu_min: float | None,
    k8s_memory_min: int | None,
    k8s_cpu_max: float | None,
    k8s_memory_max: int | None,
    k8s_devices: list[str],
    k8s_device_none: bool,
    k8s_preset: str | None,
    ssh: bool = False,
) -> Any:
    """
    Start an execution of a step.
    """
    # Having to explicitly compare to `--help` is slightly weird, but it's because of the nested command thing.
    if step_name == "--help" or not step_name:
        click.echo(ctx.get_help(), color=ctx.color)
        print_step_list(ctx, commit)
        ctx.exit()
        return
    project = get_project(require=True)
    project.refresh_details()

    if sum([watch, download_directory is not None, ssh]) > 1:
        raise click.UsageError("Only one of --watch, --sync or --ssh can be set.")

    if not commit and project.is_remote:
        # For remote projects, we need to resolve early.
        commit = project.resolve_commits()[0]["identifier"]
        info(f"Using remote project {project.name}'s newest commit {commit}")

    # We need to pass commit=None when adhoc=True to `get_config`, but
    # the further steps do need the real commit identifier from remote,
    # so this is done before `commit` is mangled by `create_adhoc_commit`.
    config = project.get_config(commit_identifier=commit, yaml_path=yaml)
    matched_step = match_step(config, step_name)
    step = config.steps[matched_step]

    commit = create_or_resolve_commit(
        project,
        commit=commit,
        adhoc=adhoc,
        allow_git_packaging=git_packaging,
        validate_adhoc_commit=validate_adhoc,
        yaml_path=yaml,
    )

    runtime_config = {}  # type: dict[str, Any]

    if bool(debug_port) ^ bool(debug_key_file):
        raise click.UsageError(
            "Both or neither of --debug-port and --debug-key-file must be set.",
        )
    if debug_port and debug_key_file:
        with open(debug_key_file) as file:
            key = file.read().strip()
            if not key.startswith("ssh"):
                raise click.UsageError(
                    f"The public key read from {debug_key_file} "
                    f"does not seem valid (it should start with `ssh`)",
                )
        runtime_config["remote_debug"] = {
            "debug_port": debug_port,
            "debug_key": key,
        }

    if autorestart:
        runtime_config["autorestart"] = autorestart

    time_limit = step.time_limit.total_seconds() if step.time_limit else None

    if k8s_devices and k8s_device_none:
        raise click.UsageError(
            "--k8s-device=(...) and --k8s-device-none cannot be used together. "
            "Using --k8s-device=(...) will discard all Kubernetes device default values on its own.",
        )

    kubernetes_dict = recursive_compact_kubernetes_dict({
        "containers": {
            "workload": {
                "resources": {
                    "requests": {
                        "cpu": k8s_cpu_min or step.resources.cpu.min,
                        "memory": k8s_memory_min or step.resources.memory.min,
                    },
                    "limits": {
                        "cpu": k8s_cpu_max or step.resources.cpu.max,
                        "memory": k8s_memory_max or step.resources.memory.max,
                        "devices": (
                            parse_environment_variable_strings(k8s_devices, coerce=int)
                            if k8s_devices
                            else EMPTY_DICT_PLACEHOLDER
                            if k8s_device_none
                            else EMPTY_DICT_PLACEHOLDER
                            if isinstance(step.resources.devices.devices, dict)
                            and step.resources.devices.devices == {}
                            else step.resources.devices.devices
                        ),
                    },
                },
            },
        },
    })
    if kubernetes_dict:
        runtime_config["kubernetes"] = kubernetes_dict

    rc = RunCommand(
        project=project,
        step=step,
        commit=commit,
        environment=environment,
        open_browser=open_browser,
        watch=watch,
        download_directory=download_directory,
        image=image,
        title=title,
        environment_variables=parse_environment_variable_strings(environment_variables),
        environment_variable_groups=environment_variable_groups,
        tags=tags,
        runtime_config=runtime_config,
        runtime_config_preset=k8s_preset,
        ssh=ssh,
        priority=priority,
        time_limit=time_limit,
    )
    with rc.make_context(rc.name, list(args), parent=ctx) as child_ctx:
        return rc.invoke(child_ctx)


def print_step_list(ctx: click.Context, commit: str | None) -> None:
    with contextlib.suppress(Exception):  # If we fail to extract the step list, it's not that big of a deal.
        config = get_project(require=True).get_config(commit_identifier=commit)
        if config.steps:
            click.secho("\nThese steps are available in the selected commit:\n", color=ctx.color, bold=True)
            for step in sorted(config.steps):
                click.echo(f"   * {step}", color=ctx.color)


def recursive_compact_kubernetes_dict(dct: dict) -> dict:
    ret = {}
    for key, value in dct.items():
        if isinstance(value, dict):
            value = recursive_compact_kubernetes_dict(value)
        if key and value not in [None, {}]:
            if value is EMPTY_DICT_PLACEHOLDER:
                value = {}
            ret[key] = value
    return ret
