from operator import itemgetter

import click

from valohai_cli.api import request
from valohai_cli.table import print_table


@click.command()
@click.option('--gpu', '-g', is_flag=True, help='Show GPU specifications.')
def environments(gpu):
    """
    List all available execution environments.
    """
    envs_data = request('get', '/api/v0/environments/', params={'limit': 9000}).json()['results']
    envs_data.sort(key=itemgetter('name'))

    columns = ['name', 'slug', 'description', 'per_hour_price_usd', 'per_user_queue_quota', 'unfinished_job_count']
    headers = ['Name', 'Slug', 'Description', 'Per-Hour USD$', 'Per-User Quota', 'Jobs in Queue']

    if gpu:
        columns = ['name', 'gpu_spec', 'per_hour_price_usd', 'per_user_queue_quota', 'unfinished_job_count']
        headers = ['Name', 'GPU Specification', 'Per-Hour USD$', 'Per-User Quota', 'Jobs in Queue']

    for env in envs_data:
        if 'per_user_queue_quota' in env and env['per_user_queue_quota'] <= 0:
            env['per_user_queue_quota'] = 'unlimited'
    print_table(
        data=envs_data,
        columns=columns,
        headers=headers,
    )
