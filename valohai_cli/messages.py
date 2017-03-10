# -- encoding: UTF-8 --
import random
from itertools import chain

import click
import six

if six.PY3:
    SUCCESS_EMOJI = [
        chr(0x1F600),  # GRINNING FACE (So) 😀
        chr(0x1F601),  # GRINNING FACE WITH SMILING EYES (So) 😁
        chr(0x1F603),  # SMILING FACE WITH OPEN MOUTH (So) 😃
        chr(0x1F604),  # SMILING FACE WITH OPEN MOUTH AND SMILING EYES (So) 😄
        chr(0x1F60A),  # SMILING FACE WITH SMILING EYES (So) 😊
        chr(0x1F60E),  # SMILING FACE WITH SUNGLASSES (So) 😎
        chr(0x1F638),  # GRINNING CAT FACE WITH SMILING EYES (So) 😸
        chr(0x1F638),  # GRINNING CAT FACE WITH SMILING EYES (So) 😸
        chr(0x1F63A),  # SMILING CAT FACE WITH OPEN MOUTH (So) 😺
        chr(0x1F63B),  # SMILING CAT FACE WITH HEART-SHAPED EYES (So) 😻
        chr(0x1F63C),  # CAT FACE WITH WRY SMILE (So) 😼
        chr(0x1F642),  # SLIGHTLY SMILING FACE (So) 🙂
    ]

    WARN_EMOJI = [
        chr(0x1F61F),  # WORRIED FACE
        chr(0x1F629),  # WEARY FACE
        chr(0x1F631),  # FACE SCREAMING IN FEAR
        chr(0x1F63E),  # POUTING CAT FACE
        chr(0x1F63F),  # CRYING CAT FACE
        chr(0x1F640),  # WEARY CAT FACE
    ]
else:
    # Can't trust the Py2 build to be wide-Unicode, so...
    SUCCESS_EMOJI = [':)', '^_^']
    WARN_EMOJI = [':(', 'o_o', '-_-']


def _format_message(message, emoji=None, prefix=None, color=None):
    return '{emoji}  {prefix} {message}'.format(
        emoji=random.choice(emoji or ['']),
        prefix=click.style(prefix, fg=color, bold=True),
        message=click.style(message, fg=color)
    )


def success(message):
    click.echo(_format_message(message, SUCCESS_EMOJI, 'Success!', 'green'))


def warn(message):
    click.echo(_format_message(message, WARN_EMOJI, 'Warning:', 'yellow'))


def format_table(data, columns=(), headers=None, sep=' | '):
    if not columns:
        columns = sorted(data[0].keys())
    if not headers:
        headers = columns
    assert len(headers) == len(columns), 'Must have equal amount of columns and headers'

    n_str = lambda s: ('' if s is None else six.text_type(s))

    # Pick the requested data and their types from the input
    printable_data = [
        [(n_str(col_val), type(col_val)) for col_val in (datum.get(column) for column in columns)]
        for datum in data
    ]

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


def print_table(data, columns=(), **kwargs):
    if isinstance(data, dict) and not columns:
        data = [{'key': key, 'value': value} for (key, value) in sorted(data.items())]
        columns = ('key', 'value')

    for y, row in enumerate(format_table(data, columns, **kwargs)):
        click.secho(row, bold=(y == 0))
        if y == 0:
            click.secho('-' * len(row), bold=True)
