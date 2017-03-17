import click

from valohai_cli.api import request
from valohai_cli.consts import yes_option
from valohai_cli.ctx import get_project, set_project_link
from valohai_cli.messages import success
from valohai_cli.utils import get_project_directory


@click.command()
@click.option('--name', '-n', prompt='Project name', required=True, help='The name for the project.')
@click.option('--description', '-d', default='', required=False, help='The description for the project.')
@click.option('--link/--no-link', '-l', default=True, help='Link the directory to the newly created project? Default yes.')
@yes_option
def create(name, description, link, yes):
    """Create a new project and optionally link it to the directory."""
    dir = get_project_directory()
    project_data = request('post', '/api/v0/projects/', data={
        'name': name,
        'description': description,
    }).json()
    success('Project {project} created.'.format(project=project_data['name']))
    if link:
        current_project = get_project(dir)
        if current_project and not yes:
            if not click.confirm(
                'The directory is already linked to {project}. Override that?'.format(
                    project=current_project.name,
                )
            ):
                return
        set_project_link(dir, project_data, inform=True)
    else:
        click.echo('Links left alone.')
