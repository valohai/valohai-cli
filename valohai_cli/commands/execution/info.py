import click

from valohai_cli.ctx import get_project
from valohai_cli.settings import settings
from valohai_cli.table import print_json, print_table
from valohai_cli.utils import humanize_identifier
from valohai_cli.utils.cli_utils import counter_argument

ignored_keys = {
    'commit',
    'counter',
    'ctime',
    'environment',
    'events',
    'id',
    'inputs',
    'metadata',
    'outputs',
    'parameters',
    'project',
    'tags',
    'url',
    'urls',
}


@click.command()
@counter_argument
def info(counter):
    """
    Show execution info.
    """
    execution = get_project(require=True).get_execution_from_counter(
        counter=counter,
        params={
            'exclude': 'metadata,events',
        },
    )
    if settings.output_format == 'json':
        return print_json(execution)

    data = {humanize_identifier(key): str(value) for (key, value) in execution.items() if key not in ignored_keys}
    data['project name'] = execution['project']['name']
    data['environment name'] = execution['environment']['name']
    print_table(data)
    print()
    print_table(
        {input['name']: '; '.join(input['urls']) for input in execution.get('inputs', ())},
        headers=('input', 'URLs'),
    )
    print()
    print_table(
        execution.get('parameters', {}),
        headers=('parameter', 'value'),
    )
    print()
