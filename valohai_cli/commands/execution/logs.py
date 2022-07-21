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
def logs(counter: str, status: bool, stderr: bool, stdout: bool, stream: bool, all: bool) -> None:
    """
    Show or stream execution event log.
    """
    project = get_project(require=True)
    assert project
    execution = project.get_execution_from_counter(counter=counter)
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
            total = events_response['total']
            warn(
                f'There are {total} events, but only the last {len(events)} are shown. '
                f'Use `--all` to fetch everything.'
            )
        for event in events:
            if event['stream'] not in accepted_streams:
                continue
            short_time = (event['time'].split('T')[1][:-4])
            cleaned_text = clean_log_line(event['message'])
            message = f'{short_time} {cleaned_text}'
            style = stream_styles.get(event['stream'], {})
            click.echo(click.style(message, **style))  # type: ignore[arg-type]
        if stream:
            lm.update_execution()
            if lm.execution['status'] in complete_execution_statuses:
                click.echo(
                    f'The execution has finished (status {execution["status"]}); stopping stream.',
                    err=True
                )
                break
            # Fetch less on subsequent queries
            limit = 100
            time.sleep(1)
        else:
            break
