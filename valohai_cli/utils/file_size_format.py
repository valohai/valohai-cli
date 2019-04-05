# Adapted from Jinja2. Jinja2 is (c) 2017 by the Jinja Team, licensed under the BSD license.

binary_prefixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
decimal_prefixes = ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']


def filesizeformat(value, binary=False):
    """Format the value like a 'human-readable' file size (i.e. 13 kB,
    4.1 MB, 102 Bytes, etc).  Per default decimal prefixes are used (Mega,
    Giga, etc.), if the second parameter is set to `True` the binary
    prefixes are used (Mebi, Gibi).
    """
    bytes = float(value)
    base = 1024 if binary else 1000
    prefixes = binary_prefixes if binary else decimal_prefixes
    if bytes == 1:
        return '1 Byte'
    elif bytes < base:
        return '%d Bytes' % bytes
    else:
        for i, prefix in enumerate(prefixes):
            unit = base ** (i + 2)
            if bytes < unit:
                return '%.1f %s' % ((base * bytes / unit), prefix)
        return '%.1f %s' % ((base * bytes / unit), prefix)
