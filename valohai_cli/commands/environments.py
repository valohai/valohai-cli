from operator import itemgetter

import click

from valohai_cli.api import request
from valohai_cli.table import print_table


@click.command()
@click.option('--gpu/--no-gpu', '-g/-G', is_flag=True, help='Show GPU specifications.')
@click.option('--price/--no-price', '-p/-P', is_flag=True, help='Show price.')
@click.option('--queue/--no-queue', '-q/-Q', is_flag=True, help='Show queue.')
@click.option('--description/--no-description', '-d/-D', default=True, is_flag=True, help='Show description.')
def environments(gpu, price, queue, description):
    """
    List all available execution environments.
    """
    envs_data = request('get', '/api/v0/environments/', params={'limit': 9000}).json()['results']
    envs_data.sort(key=itemgetter('name'))

    columns_and_headers = filter(None, [
        ('name', 'Name'),
        ('slug', 'Slug'),
        ('gpu_spec', 'GPU Specification') if gpu else None,
        ('description', 'Description') if description else None,
        ('per_hour_price_usd', 'Per-Hour USD$') if price else None,
        ('per_user_queue_quota', 'Per-User Quota') if queue else None,
        ('unfinished_job_count', 'Jobs in Queue') if queue else None,
    ])
    columns, headers = zip(*columns_and_headers)

    for env in envs_data:
        if 'per_user_queue_quota' in env and env['per_user_queue_quota'] <= 0:
            env['per_user_queue_quota'] = 'unlimited'
    print_table(
        data=envs_data,
        columns=columns,
        headers=headers,
    )
