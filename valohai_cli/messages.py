import random

import click

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


def success(message):
    message = random.choice(SUCCESS_EMOJI) + '  ' + message
    click.secho(message, fg='green')


def warn(message):
    message = random.choice(WARN_EMOJI) + '  ' + message
    click.secho(message, fg='yellow')
