from typing import Any, List, Optional

import click

from valohai_cli.api import request
from valohai_cli.commands.deployment.create_version.dynamic_creation_command import (
    CreationCommand,
)
from valohai_cli.ctx import get_project
from valohai_cli.messages import info
from valohai_cli.utils import parse_environment_variable_strings
from valohai_cli.utils.commits import create_or_resolve_commit
from valohai_cli.utils.matching import match_from_list_with_error


@click.command(
    context_settings={"ignore_unknown_options": True},
    add_help_option=False,
)
@click.option('--commit', '-c', default=None, metavar='SHA', help='The commit to use. Defaults to the current HEAD.')
@click.option('--deployment', '-d', help='The name of the deployment to use.')
@click.option('--var', '-v', 'environment_variables', multiple=True, help='Add environment variable (NAME=VALUE). May be repeated.')
@click.option('--endpoints', '-e', multiple=True, help='Names of endpoints enabled in deployment version.')
@click.option('--name', '-n', 'version_name', default=None, help='Name of the created version (defaults to a name based on the creation date).')
@click.option('--inherit-env-vars/--no-inherit-env-vars', default=True, help='Use project environment variables in deployment.')
@click.argument('args', nargs=-1, type=click.UNPROCESSED, metavar='ENDPOINT-OPTIONS...')
@click.option('--adhoc', '-a', is_flag=True, help='Upload the current state of the working directory, then create a deployment version from it.')
@click.option('--git-packaging/--no-git-packaging', '-g/-G', default=True, is_flag=True, help='When creating ad-hoc executions, whether to allow using Git for packaging directory contents.')
@click.pass_context
def create_version(
    ctx: click.Context,
    *,
    args: List[str],
    adhoc: bool,
    git_packaging: bool = True,
    commit: Optional[str],
    deployment: str,
    environment_variables: List[str],
    endpoints: List[str],
    version_name: Optional[str],
    inherit_env_vars: bool,
) -> Any:
    """
    Create a new deployment version.
    """
    project = get_project(require=True)
    project.refresh_details()
    commit = create_or_resolve_commit(
        project,
        commit=commit,
        adhoc=adhoc,
        allow_git_packaging=git_packaging,
        yaml_path=None,
    )
    deployments = request('get', '/api/v0/deployments/', params={'project': project.id}).json()['results']
    deployment_names = [d['name'] for d in deployments]
    matched_deployment_name = match_from_list_with_error(deployment_names, deployment, "deployment")
    matched_deployment = [d for d in deployments if d['name'] == matched_deployment_name][0]

    if not version_name:
        suggested_version_name: str = request('get', f'/api/v0/deployments/{matched_deployment["id"]}/suggest_version_name/').json()['name']
        info(f"Using automatically generated name {suggested_version_name}...")

    cc = CreationCommand(
        project=project,
        commit=commit,
        environment_variables=parse_environment_variable_strings(environment_variables),
        deployment=matched_deployment,
        endpoint_names=endpoints,
        version_name=version_name or suggested_version_name,
        inherit_env_vars=inherit_env_vars,
    )

    with cc.make_context(cc.name, list(args), parent=ctx) as child_ctx:
        return cc.invoke(child_ctx)
