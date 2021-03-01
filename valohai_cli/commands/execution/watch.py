import datetime
import time

import click
from click import get_current_context
from requests import RequestException

from valohai_cli.consts import stream_styles
from valohai_cli.ctx import get_project
from valohai_cli.exceptions import APIError
from valohai_cli.log_manager import LogManager
from valohai_cli.tui import Divider, Flex, Layout
from valohai_cli.utils import clean_log_line
from valohai_cli.utils.cli_utils import counter_argument


class WatchTUI:
    status_styles = {
        'started': {'fg': 'blue', 'bold': True},
        'crashed': {'fg': 'white', 'bg': 'red'},
        'stopped': {'fg': 'red'},
        'complete': {'fg': 'green', 'bold': True},
    }

    def __init__(self, execution):
        self.execution = execution
        self.log_manager = LogManager(execution)
        self.events = []
        self.n_events = 0
        self.status_text = None

    def refresh(self):
        try:
            self.log_manager.update_execution()
            event_response = self.log_manager.fetch_events(limit=100)
        except (RequestException, APIError) as err:
            self.status_text = 'Failed fetch: %s' % err
        else:
            self.status_text = None
            self.n_events = event_response['total']
            self.events.extend(event_response['events'])
            self.events = self.events[-500:]  # Only keep the last 500 events
        self.draw()

    def draw(self):
        execution = self.log_manager.execution
        events = self.events
        l = Layout()
        l.add(self.get_header_flex(execution))
        l.add(self.get_stat_flex(execution))
        l.add(Divider('='))
        available_height = l.height - len(l.rows) - 2
        if available_height > 0:
            for event in events[-available_height:]:
                l.add(
                    Flex(style=stream_styles.get(event['stream']))
                    .add(event['time'].split('T')[1][:-4] + '  ', flex=0)
                    .add(clean_log_line(event['message']), flex=4)
                )
        click.clear()
        l.draw()

    def get_stat_flex(self, execution):
        stat_flex = Flex()
        stat_flex.add(
            'Status: {status}'.format(status=execution['status']),
            style=self.status_styles.get(execution['status'], {}),
        )
        stat_flex.add('Step: {step}'.format(step=execution['step']))
        stat_flex.add('Commit: {commit}'.format(commit=execution['commit']['identifier']))
        stat_flex.add(f'{self.n_events} events', align='right')
        return stat_flex

    def get_header_flex(self, execution):
        header_flex = Flex(style={'bg': 'blue', 'fg': 'white'})
        header_flex.add(
            content='({project}) #{counter}'.format(
                project=execution['project']['name'],
                counter=execution['counter'],
            ),
            style={'bold': True},
        )
        if self.status_text:
            header_flex.add(
                content=self.status_text,
                align='center',
                style={'fg': 'black', 'bg': 'yellow'},
            )
        header_flex.add(
            content=datetime.datetime.now().isoformat(),
            align='right',
        )
        return header_flex


@click.command()
@counter_argument
def watch(counter):
    """
    Watch execution progress in a console UI.
    """
    execution = get_project(require=True).get_execution_from_counter(counter=counter)
    tui = WatchTUI(execution)
    try:
        while True:
            tui.refresh()
            time.sleep(1)
    except KeyboardInterrupt:
        get_current_context().exit()
