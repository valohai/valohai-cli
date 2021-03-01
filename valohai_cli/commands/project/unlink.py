import click

from valohai_cli.consts import yes_option
from valohai_cli.ctx import get_project
from valohai_cli.messages import success, warn
from valohai_cli.settings import settings
from valohai_cli.utils import get_project_directory


@click.command()
@yes_option
def unlink(yes):
    """
    Unlink a linked Valohai project.
    """
    dir = get_project_directory()
    project = get_project()
    if not project:
        warn(f'{dir} or its parents do not seem linked to a project.')
        return 1
    if not yes:
        click.confirm(
            'Unlink {dir} from {name}?'.format(
                dir=click.style(project.directory, bold=True),
                name=click.style(project.name, bold=True),
            ),
            abort=True,
        )
    links = settings.links.copy()
    links.pop(dir)
    settings.persistence.set('links', links)
    settings.persistence.save()
    success('Unlinked {dir} from {name}.'.format(
        dir=click.style(dir, bold=True),
        name=click.style(project.name, bold=True)
    ))
