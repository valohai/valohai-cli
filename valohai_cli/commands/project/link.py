import click

from valohai_cli.api import request
from valohai_cli.consts import yes_option
from valohai_cli.ctx import get_project
from valohai_cli.messages import success, warn
from valohai_cli.settings import settings
from valohai_cli.utils import get_project_directory


def filter_projects(projects, spec):
    spec = str(spec).lower()
    return [
        project
        for project in projects
        if project['id'].lower() == spec or project['name'].lower() == spec
    ]


def choose_project(dir, spec=None):
    """
    Choose a project, possibly interactively.

    :param dir: Directory (only used for prompts)
    :param spec: An optional search string
    :return: project object or None
    """
    projects = request('get', '/api/v0/projects/', params={'count': '1000'}).json()['results']
    if not projects:
        click.echo('Please create a project first.')
        return None

    if spec:
        projects = filter_projects(projects, spec)
        if not projects:
            warn('No projects match %s' % spec)
            return None
        if len(projects) == 1:
            return projects[0]

    for i, project in enumerate(projects, 1):
        click.echo('{number} {name} {description}'.format(
            number=click.style('[%3d]' % i, fg='cyan'),
            name=project['name'],
            description=(
                click.style('(%s)' % project['description'], dim=True)
                if project.get('description')
                else ''
            ),
        ))
    while True:
        answer = click.prompt('Which project would you like to link with {dir}?'.format(
            dir=click.style(dir, bold=True)
        ))
        if not answer.isdigit() or not (1 <= int(answer) <= len(projects)):
            click.secho('Sorry, try again.')
            continue
        break
    return projects[int(answer) - 1]


@click.command()
@click.argument('project', default=None, required=False)
@yes_option
def link(project, yes):
    """
    Link a directory with a Valohai project.
    """
    dir = get_project_directory()
    current_project = get_project(dir)
    if current_project and not yes:
        click.confirm(
            text='{dir} is already linked to project {name}; continue?'.format(
                dir=click.style(current_project.directory, bold=True),
                name=click.style(current_project.name, bold=True),
            ),
            abort=True,
        )
    project = choose_project(dir, spec=project)
    if not project:
        return 1
    links = settings.get('links', {})
    links[dir] = project
    settings['links'] = links
    assert get_project(dir).id == project['id']
    settings.save()
    success('Linked {dir} to {name}.'.format(
        dir=click.style(dir, bold=True),
        name=click.style(project['name'], bold=True)
    ))
