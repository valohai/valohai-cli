from valohai_cli.models.project import Project
from valohai_cli.utils.stop_command import StopCommand

stop = StopCommand(
    entity_name="execution",
    entity_name_plural="executions",
    counter_prefix="#",
    api_endpoint="/api/v0/executions/",
    project_get_from_counter_method=Project.get_execution_from_counter,
).as_command()
