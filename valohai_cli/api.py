import platform
from urllib.parse import urljoin, urlparse

import requests
from click.globals import get_current_context
from requests.auth import AuthBase

from valohai_cli import __version__ as VERSION
from valohai_cli.exceptions import APIError, ConfigurationError
from valohai_cli.settings import settings
from valohai_cli.utils import force_text


class TokenAuth(AuthBase):
    def __init__(self, netloc, token):
        super(TokenAuth, self).__init__()
        self.netloc = netloc
        self.token = token

    def __call__(self, request):
        if not request.headers.get('Authorization') and urlparse(request.url).netloc == self.netloc:
            if self.token:
                request.headers['Authorization'] = 'Token %s' % self.token
        return request


class APISession(requests.Session):
    def __init__(self, base_url, token=None):
        super(APISession, self).__init__()
        self.base_url = base_url
        self.base_netloc = urlparse(self.base_url).netloc
        self.auth = TokenAuth(self.base_netloc, token)
        self.headers['Accept'] = 'application/json'
        self.headers['User-Agent'] = 'valohai-cli/%s (%s)' % (
            VERSION,
            ';'.join(platform.uname()),
        )

    def prepare_request(self, request):
        url_netloc = urlparse(request.url).netloc
        if not url_netloc:
            request.url = urljoin(self.base_url, request.url)
        return super(APISession, self).prepare_request(request)

    def request(self, method, url, **kwargs):
        handle_errors = bool(kwargs.pop('handle_errors', True))
        resp = super(APISession, self).request(method, url, **kwargs)
        if handle_errors and resp.status_code >= 400:
            raise APIError(resp)
        return resp


def _get_current_api_session():
    """
    Get an API session, either from the Click context cache, or a new one from the config.

    :return: API session
    :rtype: APISession
    """
    host = settings.get('host')
    token = settings.get('token')
    if not (host and token):
        raise ConfigurationError('You\'re not logged in; try `vh login` first.')
    ctx = get_current_context(silent=True) or object()
    cache_key = force_text('_api_session_%s_%s' % (host, token))
    session = getattr(ctx, cache_key, None)
    if not session:
        session = APISession(host, token)
        setattr(ctx, cache_key, session)
    return session


def request(method, url, **kwargs):
    """
    Make an authenticated API request.

    See the documentation for `requests.Session.request()`.

    :param method: HTTP Method
    :param url: URL
    :param kwargs: Other kwargs, see `requests.Session.request()`
    :return: requests.Response
    :rtype: requests.Response
    """
    session = _get_current_api_session()
    return session.request(method, url, **kwargs)
