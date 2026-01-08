from valohai_cli.models.project import Project
from valohai_cli.utils.stop_command import StopCommand

stop = StopCommand(
    entity_name="task",
    entity_name_plural="tasks",
    counter_prefix="!",
    api_endpoint="/api/v0/tasks/",
    project_get_from_counter_method=Project.get_task_from_counter,
).as_command()
