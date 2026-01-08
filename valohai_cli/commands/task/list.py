from valohai_cli.utils.list_command import ListCommand

list = ListCommand(
    entity_name="task",
    entity_name_plural="tasks",
    counter_prefix="!",
    api_endpoint="/api/v0/tasks/",
    columns=["counter", "status", "title", "url"],
    headers=["!", "Status", "Title", "URL"],
).as_command()
