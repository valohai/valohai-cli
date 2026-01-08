from typing import Any

from valohai_cli.models.project import Project
from valohai_cli.utils.stop_command import StopCommand


class PipelineStopCommand(StopCommand):
    def get_stop_url(self, entity: dict) -> Any:
        return f"{entity['url']}/stop/"


stop = PipelineStopCommand(
    entity_name="pipeline",
    entity_name_plural="pipelines",
    counter_prefix="=",
    api_endpoint="/api/v0/pipelines/",
    project_get_from_counter_method=Project.get_pipeline_from_counter,
).as_command()
