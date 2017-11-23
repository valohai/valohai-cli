# -- encoding: UTF-8 --
import random

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

    ERROR_EMOJI = [
        chr(0x1F434),  # HORSE FACE
        chr(0x1F616),  # CONFOUNDED FACE
        chr(0x1F621),  # POUTING FACE
        chr(0x1F622),  # CRYING FACE
        chr(0x1F62D),  # LOUDLY CRYING FACE
        chr(0x1F62D),  # LOUDLY CRYING FACE
        chr(0x1F631),  # SCREAMY FACE
    ]
else:
    # Can't trust the Py2 build to be wide-Unicode, so...
    SUCCESS_EMOJI = [':)', '^_^']
    WARN_EMOJI = [':(', 'o_o', '-_-']
    ERROR_EMOJI = ['x_x', '._.', ':[']


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


def error(message):
    click.echo(_format_message(message, ERROR_EMOJI, 'ERROR:', 'red'))
