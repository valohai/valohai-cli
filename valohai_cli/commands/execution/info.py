import click

from valohai_cli.ctx import get_project
from valohai_cli.messages import print_table
from valohai_cli.utils import humanize_identifier

ignored_keys = {
    'commit',
    'counter',
    'ctime',
    'events',
    'id',
    'inputs',
    'metadata',
    'outputs',
    'parameters',
    'project',
    'url',
    'urls',
    'environment',
}


@click.command()
@click.argument('counter')
def info(counter):
    """
    Show execution info.
    """
    execution = get_project(require=True).get_execution_from_counter(counter=counter, detail=True)
    data = dict((humanize_identifier(key), str(value)) for (key, value) in execution.items() if key not in ignored_keys)
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
