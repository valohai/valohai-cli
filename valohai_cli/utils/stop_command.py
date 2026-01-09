"""
Generic stop command implementation for executions, pipelines, and tasks.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Callable

import click

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.messages import info, progress, success, warn
from valohai_cli.models.project import Project
from valohai_cli.range import IntegerRange
from valohai_cli.utils.cli_utils import HelpfulArgument


@dataclasses.dataclass(frozen=True)
class StopCommand:
    """
    Base class for stop commands that share common logic.

    :param entity_name: Singular entity name (e.g., "execution", "pipeline", "task")
    :param entity_name_plural: Plural entity name (e.g., "executions", "pipelines", "tasks")
    :param counter_prefix: Counter prefix symbol (e.g., "#", "=", "!")
    :param api_endpoint: API endpoint path (e.g., "/api/v0/executions/")
    :param project_get_from_counter_method: Name of the Project method to get entity by counter
    """

    entity_name: str
    entity_name_plural: str
    counter_prefix: str
    api_endpoint: str
    project_get_from_counter_method: Callable

    def get_entities_for_stop(
        self,
        project: Project,
        counters: list[str] | None,
        *,
        all: bool,
    ) -> list[dict]:
        """
        Get the list of entities to stop based on counters or --all flag.
        """
        params: dict[str, Any] = {"project": project.id}

        if counters == ["latest"]:
            return [self.project_get_from_counter_method(project, "latest")]

        if counters:
            params["counter"] = sorted(IntegerRange.parse(counters).as_set())
        elif all:
            params["status"] = "incomplete"
        else:
            warn(f"Nothing to stop (pass {self.counter_prefix}s or `--all`)")
            return []

        data = request("get", self.api_endpoint, params=params).json()["results"]
        assert isinstance(data, list)
        return data

    def stop_entities(
        self,
        counters: list[str] | tuple[str] | None = None,
        all: bool = False,
    ) -> None:
        """
        Stop one or more in-progress entities.
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
            raise click.UsageError(f"Pass {self.entity_name} counter(s), or `--all`, not both.")

        counters = list(counters or [])
        entities = self.get_entities_for_stop(
            project,
            counters=counters,
            all=all,
        )
        if not entities:
            info("Nothing to stop.")
            return

        for entity in entities:
            progress(f"Stopping {self.counter_prefix}{entity['counter']}... ")
            resp = request("post", self.get_stop_url(entity))
            info(resp.text)
        success("Done.")

    def get_stop_url(self, entity: dict) -> Any:
        return entity["urls"]["stop"]

    def as_command(self) -> click.Command:
        return click.Command(
            name="stop",
            callback=self.stop_entities,
            params=[
                HelpfulArgument(
                    ["counters"],
                    nargs=-1,
                    required=False,
                    help=f'Range of {self.entity_name} counters, or "latest"',
                ),
                click.Option(
                    ["--all"],
                    is_flag=True,
                    help=f"Stop all in-progress {self.entity_name_plural}.",
                ),
            ],
            help=f"Stop one or more in-progress {self.entity_name_plural}.",
        )
