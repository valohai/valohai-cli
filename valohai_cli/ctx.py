import click

from valohai_cli.exceptions import NoProject
from valohai_cli.messages import success
from valohai_cli.models.project import Project
from valohai_cli.settings import settings
from valohai_cli.utils import get_project_directory, walk_directory_parents


def get_project(dir=None, require=False):
    """
    Get the Valohai project object for a directory context.

    The object is augmented with the `dir` key.

    :param dir: Directory (defaults to cwd)
    :param require: Raise an exception if no project is found
    :return: Project object, or None.
    :rtype: valohai_cli.models.project.Project|None
    """
    links = settings.links
    if not links:
        if require:
            raise NoProject('No projects are configured')
        return None
    orig_dir = dir or get_project_directory()
    for dir in walk_directory_parents(orig_dir):
        project_obj = links.get(dir)
        if project_obj:
            return Project(data=project_obj, directory=dir)
    if require:
        raise NoProject('No project is linked to %s' % orig_dir)
    return None


def set_project_link(dir, project, inform=False):
    links = settings.links.copy()
    links[dir] = project
    settings.persistence.set('links', links)
    assert get_project(dir).id == project['id']
    settings.persistence.save()
    if inform:
        success('Linked {dir} to {name}.'.format(
            dir=click.style(dir, bold=True),
            name=click.style(project['name'], bold=True)
        ))
