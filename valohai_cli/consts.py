import click

yes_option = click.option('--yes', '-y', is_flag=True, help='Assume `yes` to confirmation prompts.')

stream_styles = {
    'status': {'fg': 'blue'},
    'stderr': {'fg': 'yellow'},
    'stdout': {'fg': 'white'},
}

incomplete_execution_statuses = {
    'created',
    'queued',
    'started',
    'stopping',
}

complete_execution_statuses = {
    'complete',
    'error',
    'crashed',
    'stopped',
}

execution_statuses = incomplete_execution_statuses | complete_execution_statuses

default_app_host = 'https://app.valohai.com/'
