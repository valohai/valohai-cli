from typing import Any, Dict, List, Optional, Tuple, Union

import click

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.messages import info, progress, success, warn
from valohai_cli.models.project import Project
from valohai_cli.range import IntegerRange
from valohai_cli.utils.cli_utils import HelpfulArgument


@click.argument(
    "counters",
    help='Range of execution counters, or "latest"',
    required=False,
    nargs=-1,
    cls=HelpfulArgument,
)
@click.option("--all", default=None, is_flag=True, help="Stop all in-progress executions.")
@click.command()
def stop(
    counters: Optional[Union[List[str], Tuple[str]]] = None,
    all: bool = False,
) -> None:
    """
    Stop one or more in-progress executions.
    """
    project = get_project(require=True)
    assert project

    if counters and len(counters) == 1 and counters[0] == "all":  # pragma: no cover
        # Makes sense to support this spelling too.
        counters = None
        all = True

    if counters and all:
        # If we spell out latest and ranges in the error message, it becomes kinda
        # unwieldy, so let's just do this.
        raise click.UsageError("Pass execution counter(s), or `--all`, not both.")

    counters = list(counters or [])
    executions = get_executions_for_stop(
        project,
        counters=counters,
        all=all,
    )

    for execution in executions:
        progress(f"Stopping #{execution['counter']}... ")
        resp = request("post", execution["urls"]["stop"])
        info(resp.text)
    success("Done.")


def get_executions_for_stop(project: Project, counters: Optional[List[str]], *, all: bool) -> List[dict]:
    params: Dict[str, Any] = {"project": project.id}
    if counters == ["latest"]:
        return [project.get_execution_from_counter("latest")]

    if counters:
        params["counter"] = sorted(IntegerRange.parse(counters).as_set())
    elif all:
        params["status"] = "incomplete"
    else:
        warn("Nothing to stop (pass #s or `--all`)")
        return []

    data = request("get", "/api/v0/executions/", params=params).json()["results"]
    assert isinstance(data, list)
    return data
