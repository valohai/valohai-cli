import os

import click
from jsonschema.exceptions import relevance
from valohai_yaml.utils import read_yaml
from valohai_yaml.validation import get_validator

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
    with open(filename, 'r') as infp:
        try:
            data = read_yaml(infp)
        except Exception as e:
            click.secho('%s: could not parse YAML: %s' % (filename, e), fg='red', bold=True)
            return 1

    validator = get_validator()
    errors = sorted(
        validator.iter_errors(data),
        key=lambda error: (relevance(error), repr(error.path)),
    )
    if not errors:
        success('%s: No errors' % filename)
        return 0
    click.secho('%s: %d errors' % (filename, len(errors)), fg='yellow', bold=True)
    for error in errors:
        simplified_schema_path = [
            el
            for el
            in list(error.relative_schema_path)[:-1]
            if el not in ('properties', 'items')
        ]
        obj_path = [str(el) for el in error.path]
        click.echo('  {validator} validation on {schema_path}: {message} ({path})'.format(
            validator=click.style(error.validator.title(), bold=True),
            schema_path=click.style('.'.join(simplified_schema_path), bold=True),
            message=click.style(error.message, fg='red'),
            path=click.style('.'.join(obj_path), bold=True),
        ))
    click.echo()
    return len(errors)


@click.command()
@click.argument('filenames', nargs=-1, type=click.Path(file_okay=True, exists=True, dir_okay=False))
def lint(filenames):
    """
    Lint (syntax-check) a valohai.yaml file.

    The return code of this command will be the total number of errors found in all the files.
    """
    if not filenames:
        config_file = os.path.join(get_project_directory(), 'valohai.yaml')
        if not os.path.exists(config_file):
            raise CLIException('There is no %s file. Pass in the names of configuration files to lint?' % config_file)
        filenames = [config_file]
    total_errors = 0
    for filename in filenames:
        total_errors += validate_file(filename)
    if total_errors:
        warn('There were %d total errors.' % total_errors)
    click.get_current_context().exit(total_errors)
