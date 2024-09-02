import click

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.models.project import Project
from valohai_cli.table import print_table


@click.command()
@click.option(
    "--summary/--no-summary",
    default=True,
    help="Show execution summary",
)
@click.option(
    "--incomplete/--no-incomplete",
    default=True,
    help="Show details of incomplete executions",
)
def status(summary: bool, incomplete: bool) -> None:
    """
    Get the general status of the linked project
    """
    project = get_project(require=True)
    project_data = request("get", f"/api/v0/projects/{project.id}/").json()

    click.secho(f"# Project {click.style(project.name, underline=True)}", bold=True)
    if "urls" in project_data:
        click.secho(f"  {project_data['urls']['display']}")
    click.secho("")

    if summary:
        print_execution_summary(project_data)
    if incomplete:
        print_incomplete_executions(project)


def print_incomplete_executions(project: Project) -> None:
    incomplete_executions = (
        request(
            "get",
            "/api/v0/executions/",
            params={
                "project": project.id,
                "status": "incomplete",
                "ordering": "counter",
            },
        )
        .json()
        .get("results", ())
    )
    if not incomplete_executions:
        return

    click.secho(f"## {len(incomplete_executions)} Incomplete Executions\n", bold=True)

    print_table(incomplete_executions, ["counter", "status", "step"], headers=["#", "Status", "Step"])


def print_execution_summary(project_data: dict) -> None:
    execution_summary = project_data.get("execution_summary", {}).copy()
    if not execution_summary:
        return
    total = execution_summary.pop("count")
    if not total:
        click.secho("No executions yet.", fg="cyan")
        return
    click.secho(f"## Summary of {total} executions\n", bold=True)
    print_table(
        [
            {"status": key.replace("_count", ""), "count": value}
            for (key, value) in sorted(execution_summary.items())
            if value
        ],
        columns=["status", "count"],
        headers=["Status", "Count"],
    )
    click.secho("\n")
