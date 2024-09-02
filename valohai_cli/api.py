import platform
from typing import Any, Optional, Tuple, Union
from urllib.parse import urljoin, urlparse

import click
import requests
from requests.auth import AuthBase
from requests.models import PreparedRequest, Request, Response

from valohai_cli import __version__ as VERSION
from valohai_cli.exceptions import (
    APIConnectionError,
    APIError,
    APINotFoundError,
    NotLoggedIn,
)
from valohai_cli.settings import settings
from valohai_cli.utils import force_text


class TokenAuth(AuthBase):
    def __init__(self, netloc: str, token: Optional[str]) -> None:
        super().__init__()
        self.netloc = netloc
        self.token = token

    def __call__(self, request: PreparedRequest) -> PreparedRequest:
        if (
            not request.headers.get("Authorization")
            and urlparse(request.url).netloc == self.netloc
            and self.token
        ):
            request.headers["Authorization"] = f"Token {self.token}"
        return request


class APISession(requests.Session):
    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        *,
        verify_ssl: Union[bool, str] = True,
    ) -> None:
        """
        :param verify_ssl: Path to a CA bundle to use,
                           or True to use the system's default CA bundle,
                           or False to disable SSL verification.
        """
        super().__init__()
        self.verify = verify_ssl
        self.base_url = base_url
        self.base_netloc = urlparse(self.base_url).netloc
        self.auth = TokenAuth(self.base_netloc, token)
        self.headers["Accept"] = "application/json"

    def get_user_agent(self) -> str:
        uname = ";".join(platform.uname())
        py_version = f"{platform.python_implementation()} {platform.python_version()}"
        user_agent = f"valohai-cli/{VERSION} on {py_version} ({uname})"
        if settings.api_user_agent_prefix:
            user_agent = f"{settings.api_user_agent_prefix} {user_agent}"
        return user_agent

    def prepare_request(self, request: Request) -> PreparedRequest:
        request.headers.setdefault("User-Agent", self.get_user_agent())
        url_netloc: str = urlparse(request.url).netloc
        if not url_netloc:
            request.url = urljoin(self.base_url, request.url)
        return super().prepare_request(request)

    def request(self, method: str, url: str, **kwargs: Any) -> Response:  # type: ignore
        api_error_class = kwargs.pop("api_error_class", APIError)
        handle_errors = bool(kwargs.pop("handle_errors", True))
        try:
            resp = super().request(method, url, **kwargs)
        except requests.ConnectionError as ce:
            if "Connection refused" in str(ce):
                host = urlparse(ce.request.url).netloc if ce.request else self.base_netloc
                msg = f"Unable to connect to {host!r} (connection refused); try again soon."
                raise APIConnectionError(msg) from ce
            raise APIConnectionError(str(ce)) from ce

        if handle_errors and resp.status_code >= 400:
            cls = APINotFoundError if resp.status_code == 404 else api_error_class
            raise cls(resp)
        return resp


def _get_current_api_session() -> APISession:
    """
    Get an API session, either from the Click context cache, or a new one from the config.
    """
    host, token = get_host_and_token()
    ctx = click.get_current_context(silent=True) or None
    cache_key: str = force_text(f"_api_session_{host}_{token}")
    session: Optional[APISession] = getattr(ctx, cache_key, None) if ctx else None
    if not session:
        session = APISession(
            base_url=host,
            token=token,
            verify_ssl=settings.verify_ssl,
        )
        if ctx:
            setattr(ctx, cache_key, session)
    return session


def get_host_and_token() -> Tuple[str, str]:
    host = settings.host
    token = settings.token
    if not (host and token):
        raise NotLoggedIn("You're not logged in; try `vh login` first.")
    return (host, token)


def request(method: str, url: str, **kwargs: Any) -> Response:
    """
    Make an authenticated API request.

    See the documentation for `requests.Session.request()`.

    :param method: HTTP Method
    :param url: URL
    :param kwargs: Other kwargs, see `APISession.request()`
    :return: requests.Response
    """
    session = _get_current_api_session()
    if url.startswith(session.base_url):
        url = url[len(session.base_url) :]
    return session.request(method, url, **kwargs)
