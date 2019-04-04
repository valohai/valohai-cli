import json
from itertools import chain

import click
import sys
import six

from valohai_cli.settings import settings

TABLE_FORMATS = ('human', 'csv', 'tsv', 'scsv', 'psv', 'json')
SV_SEPARATORS = {'csv': ',', 'tsv': '\t', 'scsv': ';', 'psv': '|'}


def n_str(s):
    return ('' if s is None else six.text_type(s).replace('\n', ' '))


def format_table(data, columns, headers, sep=' | '):
    # Pick the requested data and their types from the input
    printable_data = list(pluck_printable_data(data, columns, lambda col_val: (n_str(col_val), type(col_val))))

    # Transpose `printable_data` and count maximum length of data in each column
    column_widths = [max(len(s) for (s, t) in col) for col in zip(*printable_data)]

    # Take header lengths into account
    column_widths = [max(len(header), col_w) for (header, col_w) in zip(headers, column_widths)]

    for row in chain([headers], printable_data):
        cells = []
        for datum, width in zip(row, column_widths):
            if isinstance(datum, tuple):
                datum, tp = datum
            else:
                tp = six.text_type
            if tp in (int, float):
                datum = datum.rjust(width)
            else:
                datum = datum.ljust(width)
            cells.append(datum[:width])
        row = sep.join(cells)
        yield row.rstrip()


def pluck_printable_data(data, columns, col_formatter):
    for datum in data:
        yield [col_formatter(col_val) for col_val in (datum.get(column) for column in columns)]


def print_table(data, columns=(), headers=None, format=None, **kwargs):
    if isinstance(data, dict) and not columns:
        data = [{'key': key, 'value': value} for (key, value) in sorted(data.items())]
        columns = ('key', 'value')
    if not columns:
        columns = sorted(data[0].keys())
    if not headers:
        headers = columns
    assert len(headers) == len(columns), 'Must have equal amount of columns and headers'

    if not format:  # Auto-determine format from settings
        format = settings.table_format

    if format == 'human':
        for y, row in enumerate(format_table(data, columns, headers, **kwargs)):
            click.secho(row, bold=(y == 0))
            if y == 0:
                click.secho('-' * len(row), bold=True)
    elif format == 'json':
        json.dump(data, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    elif format in SV_SEPARATORS:
        import csv
        writer = csv.writer(sys.stdout, delimiter=SV_SEPARATORS[format], quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        writer.writerows(pluck_printable_data(data, columns, lambda col_val: n_str(col_val)))
    else:
        raise RuntimeError('Unknown print_table format: {}'.format(format))
