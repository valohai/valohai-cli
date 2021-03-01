import click
from click import prompt

from valohai_cli.api import request
from valohai_cli.consts import yes_option
from valohai_cli.ctx import get_project, set_project_link
from valohai_cli.exceptions import APINotFoundError, APIError
from valohai_cli.messages import info, success, warn
from valohai_cli.utils import get_project_directory, compact_dict

OWNER_HELP = (
    'The owner for the project. Either the name of an organization you belong to, '
    'or an organization and team, e.g. `myorg:team`.'
)


def create_project(directory, name, description='', owner=None, link=True, yes=False):
    """
    Internal API for creating a project.
    """
    project_data = request('post', '/api/v0/projects/', data=compact_dict({
        'name': name,
        'description': description,
        'owner': owner,
    })).json()
    long_name = '{}/{}'.format(
        project_data["owner"]["username"],
        project_data["name"],
    )
    success(f'Project {long_name} created.')
    if link:
        current_project = get_project(directory)
        if current_project and not yes:
            if not click.confirm(
                'The directory is already linked to {project}. Override that?'.format(
                    project=current_project.name,
                )
            ):
                return
        set_project_link(directory, project_data, inform=True)
    else:
        info('Links left alone.')


class OwnerOptionsOption(click.Option):

    def prompt_for_value(self, ctx):
        try:
            options = request('get', '/api/v0/projects/ownership_options/').json()
        except APINotFoundError:  # Endpoint not there, ah well!
            return None
        except APIError as ae:
            warn(f'Unable to retrieve ownership options: {ae}')
            return None
        if not options:
            return None
        if len(options) == 1:
            return options[0]

        print('Who should own this project? The options available to you are:')
        for option in options:
            print(f' * {option}')

        return prompt(
            self.prompt,
            default=options[0],
            type=click.Choice(options),
            show_choices=False,
            value_proc=lambda x: self.process_value(ctx, x),
        )


@click.command()
@click.option('--name', '-n', prompt='Project name', required=True, help='The name for the project.')
@click.option('--description', '-d', default='', required=False, help='The description for the project.')
@click.option('--owner', '-o', prompt='Owner', required=False, help=OWNER_HELP, cls=OwnerOptionsOption)
@click.option('--link/--no-link', '-l', default=True,
    help='Link the directory to the newly created project? Default yes.')
@yes_option
def create(name, description, link, owner, yes):
    """Create a new project and optionally link it to the directory."""
    return create_project(
        directory=get_project_directory(),
        name=name,
        description=description,
        link=link,
        owner=owner,
        yes=yes,
    )
