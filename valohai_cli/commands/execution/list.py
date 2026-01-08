from datetime import timedelta

from valohai_cli.consts import execution_statuses
from valohai_cli.utils.list_command import ListCommand


class ExecutionListCommand(ListCommand):
    def process_entity(self, entity: dict) -> None:
        super().process_entity(entity)
        if entity.get("duration"):
            entity["duration"] = str(timedelta(seconds=round(entity["duration"]))).rjust(10)
        else:
            entity["duration"] = ""


list = ExecutionListCommand(
    entity_name="execution",
    entity_name_plural="executions",
    counter_prefix="#",
    api_endpoint="/api/v0/executions/",
    columns=["counter", "status", "step", "duration", "url"],
    headers=["#", "Status", "Step", "Duration", "URL"],
    status_choices=frozenset(execution_statuses | {"incomplete"}),
).as_command()
