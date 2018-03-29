import math
import time

import click

from valohai_cli.utils import force_text


class LayoutElement:
    style = {}
    layout = None


class Divider(LayoutElement):
    """
    Full-width divider.
    """

    def __init__(self, ch='#', style=None):
        """
        :param ch: The character (or characters) to fill the line with
        :type ch: str
        :param style: Click style dictionary
        """
        self.ch = force_text(ch)
        self.style = (style or {})

    def draw(self):
        chs = (self.ch * int(math.ceil(self.layout.width / len(self.ch))))[:self.layout.width]
        click.echo(click.style(chs, **self.style))


class Flex(LayoutElement):
    """
    A columnar layout element.
    """
    aligners = {
        'left': lambda content, width: content.ljust(width),
        'right': lambda content, width: content.rjust(width),
        'center': lambda content, width: content.center(width),
    }

    def __init__(self, style=None):
        self.cells = []
        self.style = (style or {})

    def add(self, content, flex=1, style=None, align='left'):
        """
        Add a content column to the flex.

        :param content: String content
        :type content: str
        :param flex: Flex value; if 0, the column will always take as much space as its content needs.
        :type flex: int
        :param style: Click style dictionary
        :type style: dict
        :param align: Alignment for the content (left/right/center).
        :type align: str
        :return: The Flex, for chaining
        :rtype: Flex
        """
        self.cells.append({
            'content': force_text(content),
            'flex': flex,
            'style': style or {},
            'align': align,
        })
        return self

    def draw(self):
        if not self.cells:
            return
        total_flex = sum(cell['flex'] for cell in self.cells)
        static_width = sum(len(cell['content']) for cell in self.cells if cell['flex'] <= 0)
        available_width = self.layout.width - static_width
        flex_unit = available_width // total_flex
        row = []
        used_width = 0
        for i, cell in enumerate(self.cells):
            is_last = (i == len(self.cells) - 1)
            if cell['flex'] <= 0:
                width = len(cell['content'])
            else:
                width = int(cell['flex'] * flex_unit)
            if is_last:
                width = self.layout.width - used_width
            aligned_content = self.aligners[cell['align']](cell['content'], width)[:width]
            style = dict(self.style, **cell['style'])
            row.append(click.style(aligned_content, reset=True, **style))
            used_width += width
        click.echo(''.join(row))


class Layout:
    """
    Row-oriented layout.
    """

    def __init__(self):
        self.rows = []
        self.width, self.height = click.get_terminal_size()

    def add(self, element):
        """
        Add a LayoutElement to the Layout.

        :param element: The layout element to add
        :type element: LayoutElement
        :return: The Layout, for chaining
        :rtype: Layout
        """
        assert isinstance(element, LayoutElement)
        element.layout = self
        self.rows.append(element)
        return self

    def draw(self):
        """
        Draw the Layout onto screen.
        """
        self.width, self.height = click.get_terminal_size()
        for element in self.rows:
            element.draw()


def get_spinner_character():
    return '|/-\\'[int(time.time() * 3) % 4]
