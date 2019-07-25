import json

import click
import sys
import six
from click import get_terminal_size

from valohai_cli._vendor.tabulate import tabulate
from valohai_cli.settings import settings

TABLE_FORMATS = ('human', 'csv', 'tsv', 'scsv', 'psv', 'json')
SV_SEPARATORS = {'csv': ',', 'tsv': '\t', 'scsv': ';', 'psv': '|'}


def n_str(s):
    return ('' if s is None else six.text_type(s).replace('\n', ' '))


def _format(datum, width, allow_rjust=True):
    if isinstance(datum, tuple):
        datum, tp = datum
    else:
        tp = six.text_type
    if width is None:
        return str(datum)
    if tp in (int, float) and allow_rjust:
        datum = datum.rjust(width)
    else:
        datum = datum.ljust(width)
    return datum[:width]


class HumanTableFormatter:
    def __init__(self, data, columns, headers, sep=' | '):
        self.columns = columns
        self.headers = headers
        self.sep = sep

        # Pick the requested data and their types from the input
        self.printable_data = list(pluck_printable_data(data, columns, lambda col_val: (n_str(col_val), type(col_val))))

        # Transpose `printable_data` and count maximum length of data in each column
        self.column_widths = [max(len(s) for (s, t) in col) for col in zip(*self.printable_data)]

        # Take header lengths into account
        self.column_widths = [max(len(header), col_w) for (header, col_w) in zip(headers, self.column_widths)]

        self.terminal_width = get_terminal_size()[0]

        self.vertical_format = (sum(self.column_widths) >= self.terminal_width)

    def _generate_vertical(self):
        header_width = max(len(header) for header in self.headers)
        table_width = self.terminal_width - 5
        for row in self.printable_data:
            for header, value in zip(self.headers, row):
                yield (False, '{}{}{}'.format(
                    header.rjust(header_width),
                    self.sep,
                    _format(value, None),
                ).rstrip())
            yield (True, '-' * header_width)

    def _echo_vertical(self):
        sep_width = 0
        for y, (is_header, row) in enumerate(self._generate_vertical()):
            sep_width = max(sep_width, len(row))
            if y == 1 and not self.vertical_format:
                click.secho('-' * sep_width, bold=True)
            click.secho(row, bold=(is_header))

    def echo(self):
        if self.vertical_format:
            self._echo_vertical()
        else:
            print(tabulate([[val for (val, typ) in row] for row in self.printable_data], headers=self.headers))


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
        format = settings.output_format

    if format == 'human':
        htf = HumanTableFormatter(data=data, columns=columns, headers=headers, **kwargs)
        htf.echo()
    elif format == 'json':
        print_json(data)
    elif format in SV_SEPARATORS:
        import csv
        writer = csv.writer(sys.stdout, delimiter=SV_SEPARATORS[format], quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        writer.writerows(pluck_printable_data(data, columns, lambda col_val: n_str(col_val)))
    else:
        raise RuntimeError('Unknown print_table format: {}'.format(format))


def print_json(data):
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
