import click

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.utils import open_browser


@click.command()
def open():
    """
    Open the project's view in a web browser.
    """
    project = get_project(require=True)
    project_data = request('get', f'/api/v0/projects/{project.id}/').json()
    open_browser(project_data)
