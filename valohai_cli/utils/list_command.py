"""
Generic list command implementation for executions, pipelines, and tasks.
"""

from __future__ import annotations

import dataclasses
from typing import Any

import click

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.messages import info
from valohai_cli.settings import settings
from valohai_cli.table import print_json, print_table


@dataclasses.dataclass(frozen=True)
class ListCommand:
    """
    Base class for list commands that share common logic.

    :param entity_name: Singular entity name (e.g., "execution", "pipeline", "task")
    :param entity_name_plural: Plural entity name (e.g., "executions", "pipelines", "tasks")
    :param counter_prefix: Counter prefix symbol (e.g., "#", "=", "!")
    :param api_endpoint: API endpoint path (e.g., "/api/v0/executions/")
    :param columns: List of column keys to display in table
    :param headers: List of header labels for the table
    :param status_choices: Optional list of valid status values for filtering (e.g., execution_statuses)
    """

    entity_name: str
    entity_name_plural: str
    counter_prefix: str
    api_endpoint: str
    columns: list[str]
    headers: list[str]
    status_choices: frozenset[str] | None = None

    def process_entity(self, entity: dict) -> None:
        """
        Process an entity before displaying it.
        Override this method in subclasses to add custom processing.
        """
        entity["url"] = entity["urls"]["display"]

    def list_entities(
        self,
        *,
        count: int,
        deleted: bool,
        owned: bool,
        status: tuple[str, ...] | None = None,
    ) -> None:
        """
        List entities for the project.
        """
        project = get_project(require=True)
        assert project

        params: dict[str, Any] = {
            "project": project.id,
            "limit": count,
            "ordering": "-counter",
            "deleted": "false",
        }

        if status:
            params["status"] = set(status)
        if deleted:
            params["deleted"] = deleted
        if owned and settings.user:
            params["creator"] = settings.user["id"]

        entities = request("get", self.api_endpoint, params=params).json()["results"]

        if settings.output_format == "json":
            return print_json(entities)

        if not entities:
            info(f"{project}: No {self.entity_name_plural}.")
            return

        for entity in entities:
            self.process_entity(entity)

        print_table(
            entities,
            columns=self.columns,
            headers=self.headers,
        )

    def as_command(self) -> click.Command:
        params = [
            click.Option(
                ["--count", "--limit", "-n"],
                type=int,
                default=9001,
                help=f"How many {self.entity_name_plural} to show",
            ),
            click.Option(
                ["--deleted", "-d"],
                is_flag=True,
                help=f"Show only deleted {self.entity_name_plural}",
            ),
            click.Option(
                ["--owned", "-o"],
                is_flag=True,
                help=f"Show only {self.entity_name_plural} that I've created",
            ),
        ]

        # Add status option if status_choices is provided
        if self.status_choices:
            params.insert(
                0,
                click.Option(
                    ["--status"],
                    multiple=True,
                    type=click.Choice(sorted(self.status_choices)),
                    help="Filter by status (default: all)",
                ),
            )

        return click.Command(
            name="list",
            callback=self.list_entities,
            params=params,
            help=f"Show a list of {self.entity_name_plural} for the project.",
        )
