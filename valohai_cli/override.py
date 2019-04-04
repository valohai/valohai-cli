from valohai_cli.consts import default_app_host
from valohai_cli.settings import settings


def configure_token_login(host, token):
    settings.overrides['host'] = (host or default_app_host)
    settings.overrides['user'] = {'id': '<none>', 'username': '<logged in via --valohai-token>'}
    settings.overrides['token'] = token
