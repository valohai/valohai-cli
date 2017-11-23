import click

from valohai_cli.ctx import get_project
from valohai_cli.table import print_table
from valohai_cli.range import IntegerRange
from valohai_cli.utils import subset_keys


def download_execution_data(project, counters):
    executions = {}
    counters = IntegerRange.parse(counters).as_set()
    with click.progressbar(counters, label='fetching information') as counters:
        for counter in counters:
            execution = project.get_execution_from_counter(counter=counter, params={
                'exclude': 'metadata,events,tags',
            })
            executions[execution['id']] = execution
    return executions


@click.command()
@click.argument('counters', required=True, nargs=-1)
def summarize(counters):
    """
    Summarize execution metadata.

    Use the global `--table-format` switch to output JSON/TSV/CSV/...
    """
    project = get_project(require=True)
    executions = download_execution_data(project, counters)
    all_metadata_keys = set()
    all_metadata = {}
    for execution in executions.values():
        if execution['status'] in ('created', 'queued'):
            continue
        cmeta = (execution.get('cumulative_metadata') or {})
        all_metadata_keys.update(set(cmeta.keys()))
        all_metadata[execution['counter']] = (execution, cmeta)
    table_data = []
    for counter, (execution, metadata) in sorted(all_metadata.items()):
        row = subset_keys(execution, {'counter', 'id', 'duration'})
        row.update(metadata)
        table_data.append(row)
    columns = ['counter', 'duration'] + list(sorted(all_metadata_keys))
    headers = ['Execution', 'Duration'] + list(sorted(all_metadata_keys))
    print_table(table_data, columns=columns, headers=headers)
