import click
from click import Context

from typing import List, Any

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.utils import parse_environment_variable_strings
from valohai_cli.messages import success, info
from valohai_cli.settings import settings
from valohai_cli.table import print_json, print_table


@click.command()
def list() -> Any:
    """
    List environment variables of a project
    """

    project = get_project(require=True)
    data = request(method='get',url=f'/api/v0/projects/{project.id}/').json()["environment_variables"]

    if settings.output_format == 'json':
        return print_json(data)
    if not data:
        info(f'{project}: No environment variables.')
        return

    environment_variables = []

    for envvar in data :
        secret = data[envvar]["secret"]
        if(secret) :
            value = "*****"
        else :
            value = data[envvar]["value"]

        environment_variables.append({"name": envvar, "value": value, "secret": secret})

    print_table(
        environment_variables,
        columns=['name', 'value', 'secret'],
        headers=['Name', 'Value', 'Secret']
    )

