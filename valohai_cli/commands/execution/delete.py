import click
import sys

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.exceptions import APIError
from valohai_cli.messages import success, warn, progress
from valohai_cli.range import IntegerRange


@click.argument('counters', required=False, nargs=-1)
@click.option('--purge-outputs/--no-purge-outputs', help='purge outputs of the executions too')
@click.command()
def delete(counters, purge_outputs=False):
    """
    Delete one or more executions, optionally purging their outputs as well.
    """
    project = get_project(require=True)
    counters = IntegerRange.parse(counters).as_set()

    n = 0
    for counter in sorted(counters):
        if delete_execution(project, counter, purge_outputs):
            n += 1
    if n:
        success('Deleted {n} executions.'.format(n=n))
    else:
        warn('Nothing was deleted.')
        sys.exit(1)


def delete_execution(project, counter, purge_outputs=False):
    execution_url = '/api/v0/executions/{project_id}:{counter}/'.format(project_id=project.id, counter=counter)
    try:
        execution = request('get', execution_url).json()
    except APIError as ae:  # pragma: no cover
        if ae.response.status_code == 404:
            return False
        raise
    if purge_outputs:
        for output_datum in execution.get('outputs', ()):
            if not output_datum.get('purged'):
                progress('#{counter}: Purging output {name}... '.format(
                    counter=execution['counter'],
                    name=output_datum['name'],
                ))
                purge_url = '/api/v0/data/{datum_id}/purge/'.format(datum_id=output_datum['id'])
                resp = request('post', purge_url, handle_errors=False)
                if resp.status_code >= 400:  # pragma: no cover
                    warn('Error purging output: {error}; leaving this execution alone!'.format(error=resp.text))
                    return False
    progress('Deleting #{counter}... '.format(counter=execution['counter']))
    resp = request('delete', execution_url, handle_errors=False)
    if resp.status_code >= 400:  # pragma: no cover
        warn('Error deleting execution: {error}'.format(error=resp.text))
        return False
    return True
