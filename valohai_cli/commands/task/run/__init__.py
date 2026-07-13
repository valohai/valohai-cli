from __future__ import annotations

import contextlib
from typing import Any

import click
from valohai_yaml.objs.config import Config

from valohai_cli.ctx import get_project
from valohai_cli.utils import parse_environment_variable_strings
from valohai_cli.utils.cli_utils import PriorityHackCommand, priority_option
from valohai_cli.utils.commits import create_or_resolve_commit
from valohai_cli.utils.matching import match_from_list_with_error

run_epilog = (
    "More detailed help (e.g. how to define parameters and inputs) is available when you have "
    "defined which task to run. For instance, if you have a task called sweep, "
    'try running "vh task run sweep --help". (This is denoted by TASK-OPTIONS... in the usage.)'
)


@click.command(
    cls=PriorityHackCommand,
    context_settings={"ignore_unknown_options": True},
    add_help_option=False,
    epilog=run_epilog,
)
@click.argument("task_name", required=False, metavar="TASK-NAME")
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
    "--image",
    "-i",
    default=None,
    help="Override the Docker image specified in the step.",
)
@click.option(
    "--title",
    "-t",
    default=None,
    help="Title of the task.",
)
@click.option(
    "--tag",
    "tags",
    multiple=True,
    help="Tag the task. May be repeated.",
)
@click.option(
    "--adhoc",
    "-a",
    is_flag=True,
    help="Upload the current state of the working directory, then run it as an ad-hoc task.",
)
@click.option(
    "--git-packaging/--no-git-packaging",
    "-g/-G",
    default=True,
    is_flag=True,
    help="When creating ad-hoc tasks, whether to allow using Git for packaging directory contents.",
)
@click.option(
    "--include-untracked/--no-include-untracked",
    default=True,
    is_flag=True,
    help="When packaging with Git, whether to include untracked (but not ignored) files.",
)
@click.option(
    "--yaml",
    default=None,
    help="The path to the configuration YAML (valohai.yaml) file to use.",
)
@click.option(
    "--var",
    "-v",
    "environment_variables",
    multiple=True,
    help="Add environment variable (NAME=VALUE). May be repeated.",
)
@click.option(
    "--max-queued",
    type=int,
    default=None,
    help="Override maximum number of concurrently queued executions.",
)
@click.option(
    "--on-child-error",
    type=click.Choice(["continue-and-complete", "stop-all-and-error", "continue-and-error"]),
    default=None,
    help="What to do when a child execution errors.",
)
@priority_option
@click.argument(
    "args",
    nargs=-1,
    type=click.UNPROCESSED,
    metavar="TASK-OPTIONS...",
)
@click.pass_context
def run(
    ctx: click.Context,
    *,
    task_name: str | None,
    commit: str | None,
    environment: str | None,
    image: str | None,
    title: str | None,
    tags: list[str],
    adhoc: bool,
    git_packaging: bool,
    include_untracked: bool = True,
    yaml: str | None,
    environment_variables: list[str],
    max_queued: int | None,
    on_child_error: str | None,
    priority: int | None,
    args: list[str],
) -> Any:
    """
    Start a task.
    """
    if task_name == "--help" or not task_name:
        click.echo(ctx.get_help(), color=ctx.color)
        print_task_list(ctx, commit)
        ctx.exit()
        return

    project = get_project(require=True)
    project.refresh_details()

    if not commit and project.is_remote:
        from valohai_cli.messages import info

        commit = project.resolve_commits()[0]["identifier"]
        info(f"Using remote project {project.name}'s newest commit {commit}")

    config = project.get_config(commit_identifier=commit, yaml_path=yaml)
    matched_task = match_task(config, task_name)
    task = config.tasks[matched_task]
    step = config.steps.get(task.step)
    if not step:
        raise click.UsageError(
            f'Task "{matched_task}" references step "{task.step}" which is not defined in the configuration.',
        )

    commit = create_or_resolve_commit(
        project,
        commit=commit,
        adhoc=adhoc,
        allow_git_packaging=git_packaging,
        include_untracked=include_untracked,
        yaml_path=yaml,
    )

    from .dynamic_run_command import TaskRunCommand

    rc = TaskRunCommand(
        project=project,
        step=step,
        task=task,
        commit=commit,
        environment=environment,
        image=image,
        title=title,
        environment_variables=parse_environment_variable_strings(environment_variables),
        tags=tags,
        max_queued=max_queued,
        on_child_error=on_child_error,
        priority=priority,
    )
    with rc.make_context(rc.name, list(args), parent=ctx) as child_ctx:
        return rc.invoke(child_ctx)


def match_task(config: Config, task: str) -> str:
    return match_from_list_with_error(
        options=list(config.tasks),
        input=task,
        noun="task",
        param_hint="task",
    )


def print_task_list(ctx: click.Context, commit: str | None) -> None:
    with contextlib.suppress(Exception):
        config = get_project(require=True).get_config(commit_identifier=commit)
        if config.tasks:
            click.secho("\nThese tasks are available in the selected commit:\n", color=ctx.color, bold=True)
            for task_name in sorted(config.tasks):
                task = config.tasks[task_name]
                click.echo(f"   * {task_name} (step: {task.step}, type: {task.type.value})", color=ctx.color)
