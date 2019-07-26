import os
import time
from fnmatch import fnmatch

import click
import requests

from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.messages import success, warn, info
from valohai_cli.table import print_table
from valohai_cli.utils import force_text
from valohai_cli.utils.cli_utils import counter_argument
from valohai_cli.consts import complete_execution_statuses


def get_execution_outputs(execution):
    return list(request(
        method='get',
        url='/api/v0/data/',
        params={
            'output_execution': execution['id'],
            'limit': 9000,
        },
    ).json().get('results', []))


@click.command()
@counter_argument
@click.option(
    '--download', '-d', 'download_directory',
    type=click.Path(file_okay=False),
    help='Download files to this directory (by default, don\'t download). '
         'You can use `{counter}` as a placeholder that will be replaced by the execution\'s '
         'counter number.',
    default=None,
)
@click.option('--filter-download', '-f', help='Download only files matching this glob.', default=None)
@click.option('--force', is_flag=True, help='Download all files even if they already exist.')
@click.option('--sync', '-s', is_flag=True, help='Keep watching for new output files to download.')
def outputs(counter, download_directory, filter_download, force, sync):
    """
    List and download execution outputs.
    """
    if download_directory:
        download_directory = download_directory.replace("{counter}", str(counter))

    if sync:
        watch(counter, force, filter_download, download_directory)
        return

    project = get_project(require=True)
    execution = project.get_execution_from_counter(
        counter=counter,
        params={'exclude': 'outputs'},
    )
    outputs = get_execution_outputs(execution)
    if not outputs:
        warn('The execution has no outputs.')
        return
    for output in outputs:
        output['datum_url'] = 'datum://{}'.format(output['id'])
    print_table(outputs, ('name', 'datum_url', 'size'))
    if download_directory:
        outputs = filter_outputs(outputs, download_directory, filter_download, force)
        download_outputs(outputs, download_directory, show_success_message=True)


def watch(counter, force, filter_download, download_directory):
    if download_directory:
        info("Downloading to: %s\nWaiting for new outputs..." % download_directory)
    else:
        warn('Target folder is not set. Use --download to set it.')
        return

    project = get_project(require=True)
    execution = project.get_execution_from_counter(
        counter=counter,
        params={'exclude': 'outputs'},
    )
    while True:
        outputs = get_execution_outputs(execution)
        outputs = filter_outputs(outputs, download_directory, filter_download, force)
        if outputs:
            download_outputs(outputs, download_directory, show_success_message=False)
        if execution['status'] in complete_execution_statuses:
            info('Execution has finished.')
            return
        time.sleep(1)


def filter_outputs(outputs, download_directory, filter_download, force):
    if filter_download:
        outputs = [output for output in outputs if fnmatch(output['name'], filter_download)]
    if not force:
        # Do not download files that already exist
        outputs = [output for output in outputs if not os.path.isfile(os.path.join(download_directory, output['name']))]
    return outputs


def download_outputs(outputs, output_path, show_success_message=True):
    total_size = sum(o['size'] for o in outputs)
    num_width = len(str(len(outputs)))  # How many digits required to print the number of outputs
    start_time = time.time()
    with \
        click.progressbar(length=total_size, show_pos=True, item_show_func=force_text) as prog, \
        requests.Session() as dl_sess:
        for i, output in enumerate(outputs, 1):
            url = request(
                method='get',
                url='/api/v0/data/{id}/download/'.format(id=output['id']),
            ).json()['url']
            out_path = os.path.join(output_path, output['name'])
            out_dir = os.path.dirname(out_path)
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)
            resp = dl_sess.get(url, stream=True)
            resp.raise_for_status()
            prog.current_item = '(%*d/%-*d) %s' % (num_width, i, num_width, len(outputs), output['name'])
            prog.short_limit = 0  # Force visible bar for the smallest of files
            with open(out_path, 'wb') as outf:
                for chunk in resp.iter_content(chunk_size=131072):
                    prog.update(len(chunk))
                    outf.write(chunk)

    duration = time.time() - start_time
    if show_success_message:
        success('Downloaded {n} outputs ({size} bytes) in {duration} seconds'.format(
            n=len(outputs),
            size=total_size,
            duration=round(duration, 2),
        ))
