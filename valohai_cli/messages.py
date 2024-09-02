import random
import sys
from typing import List, Optional

import click

SUCCESS_EMOJI = [":)", "^_^"]
WARN_EMOJI = [":(", "o_o", "-_-"]
ERROR_EMOJI = ["x_x", "._.", ":["]
PROGRESS_EMOJI = ["..."]

if sys.platform != "win32":
    # The default Win32 console can't display these properly.

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

    PROGRESS_EMOJI = [
        chr(0x231B),  # HOURGLASS
    ]


def _format_message(
    message: str,
    emoji: Optional[List[str]] = None,
    prefix: Optional[str] = None,
    color: Optional[str] = None,
) -> str:
    selected_emoji = random.choice(emoji or [""])
    formatted_prefix = click.style(prefix, fg=color, bold=True) if prefix else ""
    formatted_message = click.style(message, fg=color)
    return f"{selected_emoji}  {formatted_prefix} {formatted_message}"


def info(message: str, err: bool = True) -> None:
    click.echo(_format_message(message, ["=>"], color="cyan"), err=err)


def success(message: str, err: bool = True) -> None:
    click.echo(_format_message(message, SUCCESS_EMOJI, "Success!", "green"), err=err)


def warn(message: str, err: bool = True) -> None:
    click.echo(_format_message(message, WARN_EMOJI, "Warning:", "yellow"), err=err)


def error(message: str, err: bool = True) -> None:
    click.echo(_format_message(message, ERROR_EMOJI, "ERROR:", "red"), err=err)


def progress(message: str, err: bool = True) -> None:
    click.echo(_format_message(message, PROGRESS_EMOJI, None, None), err=err)


DEFAULT_BANNER_STYLE = {"fg": "magenta", "bold": True}


def banner(message: str, banner_char: str = "=", banner_style: Optional[dict] = None) -> None:
    if banner_style is None:
        banner_style = DEFAULT_BANNER_STYLE

    longest_line_len = max(len(line) for line in click.unstyle(message).splitlines())

    banner_line = banner_char * longest_line_len
    click.secho(banner_line, **banner_style)
    click.echo(message)
    click.secho(banner_line, **banner_style)
