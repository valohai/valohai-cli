import re

# See Roi for type hints for these functions.


def _match_string(str, pattern):
    if str is None:
        return False
    if isinstance(pattern, re.Pattern):
        return pattern.match(str)
    return (str == pattern)


def match_error(
    response_data,
    code=None,
    message=None,
    matcher=None,
):
    if code and not _match_string(response_data.get('code'), code):
        return None
    if message and not _match_string(response_data.get('message'), message):
        return None
    if matcher and not matcher(message):
        return None
    return response_data


def find_error(
    response_data,
    code=None,
    message=None,
    matcher=None,
):
    iterable = None
    if isinstance(response_data, str):
        return match_error({'message': response_data, 'code': None}, code=code, message=message, matcher=matcher)

    if isinstance(response_data, dict):
        if 'code' in response_data and 'message' in response_data:  # Smells like the actual error object
            return match_error(response_data, code=code, message=message, matcher=matcher)
        iterable = response_data.values()
    elif isinstance(response_data, list):
        iterable = response_data

    if iterable is not None:
        for value in iterable:
            rv = find_error(value, code=code, message=message, matcher=matcher)
            if rv:
                return rv
    return None
