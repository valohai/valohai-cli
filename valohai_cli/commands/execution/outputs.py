import os
import time
from fnmatch import fnmatch

import click
import requests

from valohai_cli.ctx import get_project
from valohai_cli.messages import success, warn
from valohai_cli.table import print_table
from valohai_cli.utils import force_text


@click.command()
@click.argument('counter')
@click.option('--download', '-d', type=click.Path(file_okay=False),
              help='download files to this directory (by default, don\'t download)', default=None)
@click.option('--filter-download', '-f', help='download only files matching this glob', default=None)
def outputs(counter, download, filter_download):
    """
    List and download execution outputs.
    """
    execution = get_project(require=True).get_execution_from_counter(counter=counter)
    outputs = execution.get('outputs', ())
    if not outputs:
        warn('The execution has no outputs.')
        return
    print_table(outputs, ('name', 'url', 'size'))
    if download:
        if filter_download:
            outputs = [output for output in outputs if fnmatch(output['name'], filter_download)]
        download_outputs(outputs, download)


def download_outputs(outputs, output_path):
    if not outputs:
        warn('Nothing to download.')
        return
    total_size = sum(o['size'] for o in outputs)
    num_width = len(str(len(outputs)))  # How many digits required to print the number of outputs
    start_time = time.time()
    with \
            click.progressbar(length=total_size, show_pos=True, item_show_func=force_text) as prog, \
            requests.Session() as dl_sess:
        for i, output in enumerate(outputs, 1):
            url = output['url']
            out_path = os.path.join(output_path, output['name'])
            out_dir = os.path.dirname(out_path)
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)
            resp = dl_sess.get(url, stream=True)
            resp.raise_for_status()
            prog.current_item = '(%*d/%-*d) %s' % (num_width, i, num_width, len(outputs), output['name'])
            with open(out_path, 'wb') as outf:
                for chunk in resp.iter_content(chunk_size=131072):
                    prog.update(len(chunk))
                    outf.write(chunk)
    duration = time.time() - start_time
    success('Downloaded {n} outputs ({size} bytes) in {duration} seconds'.format(
        n=len(outputs),
        size=total_size,
        duration=round(duration, 2),
    ))
