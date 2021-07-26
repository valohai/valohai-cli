from typing import List, Union

import click

Formattable = Union[dict, list, str]

class ErrorFormatter:
    indent = '  '
    generic_dict_keys = ['non_field_errors', 'detail', 'error']

    def __init__(self) -> None:
        self.buffer: List[str] = []
        self.level: int = 0

    def write(self, prefix: str, line: str) -> None:
        indent_str = self.indent * self.level
        self.buffer.append(f"{indent_str}{prefix}{line}")

    def format(self, data: Formattable, indent: int = 0, prefix: str = '') -> None:
        self.level += indent
        if isinstance(data, dict):
            if data.get('message'):
                self.write(prefix, '{message} {styled_code}'.format(
                    message=data['message'],
                    styled_code=(
                        click.style('(code: {code})'.format(code=data.get('code')), dim=True)
                        if data.get('code')
                        else ''
                    ),
                ))
            else:
                self._format_dict(data, prefix=prefix)
        elif isinstance(data, list):
            for item in data:
                self.format(item, prefix='* ')
        else:
            self.write(prefix, data)
        self.level -= indent

    def _format_dict(self, data: dict, prefix: str = '') -> None:
        data = data.copy()
        # Peel off our generic keys first
        for key in self.generic_dict_keys:
            value = data.pop(key, None)
            if value:
                self.format(value)
        # Then format the rest
        for key, value in sorted(data.items()):
            if isinstance(value, str):
                self.write(prefix, f'{key}: {value}')
            else:
                self.write(prefix, f'{key}:')
                self.format(value, indent=1)


def format_error_data(data: Formattable) -> str:
    ef = ErrorFormatter()
    ef.format(data)
    return '\n'.join(ef.buffer)
