from valohai_cli.utils.list_command import ListCommand

list = ListCommand(
    entity_name="pipeline",
    entity_name_plural="pipelines",
    counter_prefix="=",
    api_endpoint="/api/v0/pipelines/",
    columns=["counter", "status", "title", "url"],
    headers=["=", "Status", "Title", "URL"],
).as_command()
