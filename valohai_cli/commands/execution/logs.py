import time

import click

from valohai_cli.consts import complete_execution_statuses, stream_styles
from valohai_cli.ctx import get_project
from valohai_cli.log_manager import LogManager
from valohai_cli.messages import warn
from valohai_cli.utils import clean_log_line
from valohai_cli.utils.cli_utils import counter_argument


@click.command()
@counter_argument
@click.option('--status/--no-status', default=True, help='Show status messages')
@click.option('--stderr/--no-stderr', default=True, help='Show stderr messages')
@click.option('--stdout/--no-stdout', default=True, help='Show stdout messages')
@click.option('--stream/--no-stream', default=False, help='Watch and wait for new messages?')
@click.option('--all/--no-all', default=False, help='Get all messages? This may take a while.')
def logs(counter, status, stderr, stdout, stream, all):
    """
    Show or stream execution event log.
    """
    execution = get_project(require=True).get_execution_from_counter(counter=counter)
    accepted_streams = {v for v in [
        'status' if status else None,
        'stderr' if stderr else None,
        'stdout' if stdout else None,
    ] if v}
    lm = LogManager(execution)
    limit = (0 if all else None)
    while True:
        events_response = lm.fetch_events(limit=limit)
        events = events_response['events']
        if not stream and events_response.get('truncated'):
            warn(
                'There are {total} events, but only the last {n} are shown. Use `--all` to fetch everything.'.format(
                    total=events_response['total'],
                    n=len(events),
                )
            )
        for event in events:
            if event['stream'] not in accepted_streams:
                continue
            message = '{short_time} {text}'.format(
                short_time=(event['time'].split('T')[1][:-4]),
                text=clean_log_line(event['message']),
            )
            style = stream_styles.get(event['stream'], {})
            click.echo(click.style(message, **style))
        if stream:
            lm.update_execution()
            if lm.execution['status'] in complete_execution_statuses:
                click.echo(
                    'The execution has finished (status {status}); stopping stream.'.format(
                        status=execution['status'],
                    ),
                    err=True
                )
                break
            # Fetch less on subsequent queries
            limit = 100
            time.sleep(1)
        else:
            break
