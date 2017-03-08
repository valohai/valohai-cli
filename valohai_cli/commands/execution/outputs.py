import os
import time

import click
import requests

from valohai_cli.ctx import get_project
from valohai_cli.messages import print_table, success, warn
from valohai_cli.utils import ensure_absolute_url, force_text


@click.command()
@click.argument('counter')
@click.option('--download', '-d', type=click.Path(file_okay=False),
              help='download files to this directory', default=None)
def outputs(counter, download):
    """
    List and download execution outputs.
    """
    exec = get_project(require=True).get_execution_from_counter(counter=counter, detail=True)
    outputs = exec.get('outputs', ())
    if not outputs:
        warn('The execution has no outputs.')
        return
    print_table(outputs, ('name', 'url', 'size'))
    if download:
        download_outputs(outputs, download)


def download_outputs(outputs, output_path):
    total_size = sum(o['size'] for o in outputs)
    num_width = len(str(len(outputs)))  # How many digits required to print the number of outputs
    start_time = time.time()
    with \
            click.progressbar(length=total_size, show_pos=True, item_show_func=force_text) as prog, \
            requests.Session() as dl_sess:
        for i, output in enumerate(outputs, 1):
            url = ensure_absolute_url(output['url'])
            out_path = os.path.join(output_path, output['name'])
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
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
