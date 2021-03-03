import json
import sys

import click
from click import get_terminal_size

from valohai_cli.settings import settings
from typing import Union, Tuple, Any, Iterable, Optional, Callable, List, Type, Sequence

TABLE_FORMATS = ('human', 'csv', 'tsv', 'scsv', 'psv', 'json')
SV_SEPARATORS = {'csv': ',', 'tsv': '\t', 'scsv': ';', 'psv': '|'}


def n_str(s: Union[float, str, int]) -> str:
    if s is None:
        return ''
    return str(s).replace('\n', ' ')


def _format(datum: Union[Tuple[str, Any], str], width: Optional[int], allow_rjust: bool = True) -> str:
    if isinstance(datum, tuple):
        datum, datatype = datum
    else:
        datatype = str
    if width is None:
        return str(datum)
    if datatype in (int, float) and allow_rjust:
        datum = datum.rjust(width)
    else:
        datum = datum.ljust(width)
    return datum[:width]


class HumanTableFormatter:
    def __init__(self, data: Sequence[dict], columns: Sequence[str], headers: Sequence[str], sep: str =' | ') -> None:
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

    def _generate_vertical(self) -> Iterable[Tuple[bool, str]]:
        header_width = max(len(header) for header in self.headers)
        for row in self.printable_data:
            for header, value in zip(self.headers, row):
                yield (False, '{}{}{}'.format(
                    header.rjust(header_width),
                    self.sep,
                    _format(value, None),
                ).rstrip())
            yield (True, '-' * header_width)

    def _echo_vertical(self) -> None:
        sep_width = 0
        for y, (is_header, row) in enumerate(self._generate_vertical()):
            sep_width = max(sep_width, len(row))
            if y == 1 and not self.vertical_format:
                click.secho('-' * sep_width, bold=True)
            click.secho(row, bold=(is_header))

    def echo(self) -> None:
        if self.vertical_format:
            self._echo_vertical()
            return
        from valohai_cli._vendor.tabulate import tabulate  # type: ignore[attr-defined]
        tabulable_data = [[val for (val, typ) in row] for row in self.printable_data]
        print(tabulate(tabulable_data, headers=self.headers))


StringAndType = Tuple[str, Type]


def pluck_printable_data(
    data: Sequence[dict],
    columns: Sequence[str],
    col_formatter: Callable[[Any], StringAndType],
) -> Iterable[List[StringAndType]]:
    for datum in data:
        yield [col_formatter(col_val) for col_val in (datum.get(column) for column in columns)]


def print_table(
    data: Any,
    columns: Sequence[str] = (),
    headers: Optional[Sequence[str]] = None,
    format: Optional[str] = None,
    **kwargs: Any,
) -> None:
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
        writer.writerows(pluck_printable_data(data, columns, lambda col_val: (n_str(col_val), str)))
    else:
        raise RuntimeError(f'Unknown print_table format: {format}')


def print_json(data: Any) -> None:
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
