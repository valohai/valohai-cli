import click

from valohai_cli.api import APISession
from valohai_cli.consts import yes_option, default_app_host
from valohai_cli.messages import success
from valohai_cli.settings import settings


@click.command()
@click.option('--username', '-u', prompt=True)
@click.option('--password', '-p', prompt=True, hide_input=True)
@click.option('--host', '-h', default=default_app_host)
@yes_option
def login(username, password, host, yes):
    """Log in into Valohai."""
    if settings.user and settings.token and not yes:
        user = settings.user
        message = (
            'You are already logged in as {username}.\n'
            'Are you sure you wish to acquire a new token?'
        ).format(username=user['username'])
        click.confirm(message, abort=True)
    with APISession(host) as sess:
        token_data = sess.post('/api/v0/get-token/', data={'username': username, 'password': password}).json()
        token = token_data['token']
    with APISession(host, token) as sess:
        user_data = sess.get('/api/v0/users/me/').json()
    settings.persistence.update(host=host, user=user_data, token=token)
    settings.persistence.save()
    success('Logged in. Hi!')
