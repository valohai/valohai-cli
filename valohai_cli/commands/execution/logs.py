import time

import click

from valohai_cli.api import request
from valohai_cli.consts import complete_execution_statuses, stream_styles
from valohai_cli.ctx import get_project


@click.command()
@click.argument('counter')
@click.option('--status/--no-status', default=True, help='Show status messages')
@click.option('--stderr/--no-stderr', default=True, help='Show stderr messages')
@click.option('--stdout/--no-stdout', default=True, help='Show stdout messages')
@click.option('--stream/--no-stream', default=False, help='Watch and wait for new messages?')
def logs(counter, status, stderr, stdout, stream):
    """
    Show or stream execution event log.
    """
    execution = get_project(require=True).get_execution_from_counter(counter=counter)
    detail_url = execution['url']

    accepted_streams = set(v for v in [
        'status' if status else None,
        'stderr' if stderr else None,
        'stdout' if stdout else None,
    ] if v)
    seen_events = set()
    while True:
        execution = request('get', detail_url, params={'exclude': 'metadata'}).json()
        events = execution.get('events', ())
        for event in events:
            event_id = (event['stream'], event['time'])
            if event_id in seen_events:
                continue
            seen_events.add(event_id)
            if event['stream'] not in accepted_streams:
                continue
            message = '{short_time} {text}'.format(
                short_time=(event['time'].split('T')[1][:-4]),
                text=(event['message']),
            )
            style = stream_styles.get(event['stream'], {})
            click.echo(click.style(message, **style))
        if stream:
            if execution['status'] in complete_execution_statuses:
                click.echo(
                    'The execution has finished (status {status}); stopping stream.'.format(
                        status=execution['status'],
                    ),
                    err=True
                )
                break
            time.sleep(1)
        else:
            break
