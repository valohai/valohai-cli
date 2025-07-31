from __future__ import annotations

import math
import shutil
import time
from typing import Any, Callable

import click

from valohai_cli.utils import force_text


class LayoutElement:
    style: dict[str, Any] = {}
    layout: Layout

    def draw(self) -> None:
        raise NotImplementedError(f"{self.__class__} must implement draw()")


class Divider(LayoutElement):
    """
    Full-width divider.
    """

    def __init__(self, ch: str = "#", style: dict[str, Any] | None = None) -> None:
        """
        :param ch: The character (or characters) to fill the line with
        :param style: Click style dictionary
        """
        self.ch = force_text(ch)
        self.style = style or {}

    def draw(self) -> None:
        chs = (self.ch * int(math.ceil(self.layout.width / len(self.ch))))[: self.layout.width]
        click.echo(click.style(chs, **self.style))


class Flex(LayoutElement):
    """
    A columnar layout element.
    """

    aligners: dict[str, Callable[[str, int], str]] = {
        "left": lambda content, width: content.ljust(width),
        "right": lambda content, width: content.rjust(width),
        "center": lambda content, width: content.center(width),
    }

    def __init__(self, style: dict[str, Any] | None = None) -> None:
        self.cells: list[dict] = []
        self.style = style or {}

    def add(
        self,
        content: str = "",
        *,
        flex: int = 1,
        style: dict | None = None,
        align: str = "left",
    ) -> Flex:
        """
        Add a content column to the flex.

        :param content: String content
        :param flex: Flex value; if 0, the column will always take as much space as its content needs.
        :param style: Click style dictionary
        :param align: Alignment for the content (left/right/center).
        :return: The Flex, for chaining
        """
        self.cells.append({
            "content": force_text(content),
            "flex": flex,
            "style": style or {},
            "align": align,
        })
        return self

    def draw(self) -> None:
        if not self.cells:
            return
        total_flex = sum(cell["flex"] for cell in self.cells)
        static_width = sum(len(cell["content"]) for cell in self.cells if cell["flex"] <= 0)
        available_width = self.layout.width - static_width
        flex_unit = available_width // total_flex
        row = []
        used_width = 0
        for i, cell in enumerate(self.cells):
            is_last = i == len(self.cells) - 1
            if cell["flex"] <= 0:  # noqa: SIM108
                width = len(cell["content"])
            else:
                width = int(cell["flex"] * flex_unit)
            if is_last:
                width = self.layout.width - used_width
            aligned_content = self.aligners[cell["align"]](cell["content"], width)[:width]
            style = dict(self.style, **cell["style"])
            row.append(click.style(aligned_content, reset=True, **style))
            used_width += width
        click.echo("".join(row))


class Layout:
    """
    Row-oriented layout.
    """

    def __init__(self) -> None:
        self.rows: list[LayoutElement] = []
        self.width, self.height = shutil.get_terminal_size()

    def add(self, element: LayoutElement) -> Layout:
        """
        Add a LayoutElement to the Layout.

        :param element: The layout element to add
        :return: The Layout, for chaining
        """
        assert isinstance(element, LayoutElement)
        element.layout = self
        self.rows.append(element)
        return self

    def draw(self) -> None:
        """
        Draw the Layout onto screen.
        """
        self.width, self.height = shutil.get_terminal_size()
        for element in self.rows:
            element.draw()


def get_spinner_character() -> str:
    return "|/-\\"[int(time.time() * 3) % 4]
