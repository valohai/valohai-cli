import os

import click
from valohai_yaml.lint import lint_file

from valohai_cli.ctx import get_project
from valohai_cli.exceptions import CLIException
from valohai_cli.messages import success, warn
from valohai_cli.utils import get_project_directory


def validate_file(filename):
    """
    Validate `filename`, print its errors, and return the number of errors.

    :param filename: YAML filename
    :type filename: str
    :return: Number of errors
    :rtype: int
    """
    lr = lint_file(filename)

    if not lr.messages:
        success('%s: No errors' % filename)
        return 0
    click.secho('{filename}: {error_count} errors, {warning_count} warnings'.format(
        filename=filename,
        error_count=lr.error_count,
        warning_count=lr.warning_count,
    ), fg='yellow', bold=True)
    for message in lr.messages:
        click.echo('  {type}: {message}'.format(**message))
    click.echo()
    return lr.error_count


@click.command()
@click.argument('filenames', nargs=-1, type=click.Path(file_okay=True, exists=True, dir_okay=False))
def lint(filenames):
    """
    Lint (syntax-check) a valohai.yaml file.

    The return code of this command will be the total number of errors found in all the files.
    """
    if not filenames:
        project = get_project()
        directory = (project.directory if project else get_project_directory())
        config_file = os.path.join(directory, 'valohai.yaml')
        if not os.path.exists(config_file):
            raise CLIException('There is no %s file. Pass in the names of configuration files to lint?' % config_file)
        filenames = [config_file]
    total_errors = 0
    for filename in filenames:
        total_errors += validate_file(filename)
    if total_errors:
        warn('There were %d total errors.' % total_errors)
    click.get_current_context().exit(total_errors)
