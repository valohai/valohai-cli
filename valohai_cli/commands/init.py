import os
import sys

import click

from valohai_cli.api import get_host_and_token
from valohai_cli.commands.project.create import create
from valohai_cli.commands.project.link import link
from valohai_cli.ctx import get_project
from valohai_cli.exceptions import NotLoggedIn
from valohai_cli.messages import error, warn
from valohai_cli.utils import get_project_directory
from valohai_cli.yaml_wizard import yaml_wizard

DONE_TEXT = """
All done! You can now create an ad-hoc execution with
  $ {command}
to see that everything works as it should.
For better repeatability, we recommend that your code
is in a Git repository; you can link the repository
to the project in the Valohai webapp.

Happy (machine) learning!
"""


@click.command()
def init():
    """
    Interactively initialize a Valohai project.
    """
    project = get_project()
    if project:
        error(
            'The directory {directory} is already linked to {name}. Please unlink the directory first.'.format(
                directory=project.directory,
                name=project.name,
            )
        )
        sys.exit(1)

    click.secho('Hello! This wizard will help you start a Valohai compatible project.', fg='green', bold=True)
    directory = get_project_directory()
    if not click.confirm(
        'First, let\'s make sure {dir} is the root directory of your project. Is that correct?'.format(
            dir=click.style(directory, bold=True),
        )
    ):  # pragma: no cover
        click.echo('Alright! Please change to the root directory of your project and try again.')
        return

    valohai_yaml_path = os.path.join(directory, 'valohai.yaml')

    if not os.path.isfile(valohai_yaml_path):
        click.echo('Looks like you don\'t have a Valohai.yaml file. Let\'s create one!')
        yaml_wizard(directory)
    else:
        click.echo('There is a Valohai.yaml file in this directory, so let\'s skip the creation wizard.')

    try:
        get_host_and_token()
    except NotLoggedIn:  # pragma: no cover
        error('Please log in with `vh login` before continuing.')
        sys.exit(3)

    project = link_or_create_prompt(directory)

    if not project:
        # If we didn't link or create a project, don't show the "all good to go" text.
        return

    width = min(70, click.get_terminal_size()[0])
    click.secho('*' * width, fg='green', bold=True)
    click.echo(DONE_TEXT.strip().format(
        command=click.style('vh exec run --adhoc --watch execute', bold=True),
    ))
    click.secho('*' * width, fg='green', bold=True)


def link_or_create_prompt(cwd):
    while True:
        response = click.prompt(
            'Do you want to link this directory to a pre-existing project, or create a new one? [L/C]\n'
            'If you\'d prefer to do neither at this point, respond [N].'
        ).lower().strip()
        if response.startswith('l'):
            link.main(prog_name='vh-link', args=[], standalone_mode=False)
        elif response.startswith('c'):
            create.main(prog_name='vh-create', args=[], standalone_mode=False)
        elif response.startswith('n'):
            click.echo(
                'Okay, skipping linking or creating a project for the time being.\n'
                'You can do that later with `vh project link` or `vh project create`.'
            )
            return None
        else:
            warn('Sorry, I couldn\'t understand that.')
            continue
        project = get_project(cwd)
        if not project:
            error('Oops, looks like something went wrong.')
            sys.exit(2)
        return project
