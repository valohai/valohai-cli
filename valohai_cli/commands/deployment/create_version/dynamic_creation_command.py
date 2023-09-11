from typing import Any, Dict, List, Optional
from uuid import UUID

import click
import valohai_yaml
from click.core import Option
from valohai_yaml.objs import File

from valohai_cli.api import request
from valohai_cli.commands.execution.run.dynamic_run_command import (
    generate_sanitized_options,
)
from valohai_cli.messages import error, success
from valohai_cli.models.project import Project
from valohai_cli.utils import (
    humanize_identifier,
    parse_environment_variable_strings,
    sanitize_option_name,
)

DATUM_URI_PREFIX = 'datum://'


class CreationCommand(click.Command):
    """
    A dynamically-generated subcommand that has Click options for files for deployments.
    """

    def __init__(
        self,
        project: Project,
        deployment: Dict[str, Any],
        endpoint_names: List[str],
        commit: str,
        version_name: str,
        inherit_env_vars: bool = True,
        environment_variables: Optional[Dict[str, str]] = None,
    ) -> None:
        self.project = project
        self.deployment = deployment
        self.endpoint_names = endpoint_names
        self.commit = commit
        self.version_name = version_name
        self.environment_variables = dict(environment_variables or {})
        self.inherit_env_vars = inherit_env_vars
        super().__init__(
            name=sanitize_option_name(deployment['name'].lower()),
            callback=self.execute,
            add_help_option=True,
        )

        commit_config = request(
            method='get',
            url=f'/api/v0/commits/{commit}/',
            params={'include': 'config'},
        ).json()
        self.config = valohai_yaml.parse(commit_config['config'])

        for endpoint in self.config.endpoints.values():
            if endpoint.name in self.endpoint_names:
                for file in endpoint.files:
                    self.params.append(self.convert_file_to_option(endpoint_name=endpoint.name, file=file))

    def convert_file_to_option(self, endpoint_name: str, file: File) -> Option:
        """
        Convert an endpoint file into a click Option.
        """
        name = f"{endpoint_name}.{file.name}"
        option = click.Option(
            param_decls=list(generate_sanitized_options(name)),
            required=True,
            metavar='URL',
            help=f'File "{humanize_identifier(name)}"',
        )
        option.name = f"^{name}"
        option.help_group = 'File Options'  # type: ignore[attr-defined]
        return option

    def execute(self, **kwargs: Any) -> None:
        """
        Execute the creation of the deployment version.

        This is the Click callback for this command.

        :param kwargs: Assorted kwargs (as passed in by Click).
        :return: Naught
        """
        payload = {
            'commit': self.commit,
            'deployment': self.deployment['id'],
            'environment_variables': parse_environment_variable_strings(self.environment_variables),
            'inherit_environment_variables': self.inherit_env_vars,
            'name': self.version_name,
            'enabled': True,
        }

        endpoint_configurations: Dict[str, Any] = {}
        endpoint_names_from_config = {e.name for e in self.config.endpoints.values()}
        for name in self.endpoint_names:
            if name not in endpoint_names_from_config:
                raise ValueError(f"No endpoint named {name} present in commit configuration.")
            endpoint_configurations[name] = {
                'enabled': True,
                'files': {},  # These will be filled in during the following loop
                'replicas': 1,
            }

        for key, value in kwargs.items():
            if key.startswith('^'):
                designated_endpoint, filename = key[1:].split('.')
                if designated_endpoint in endpoint_configurations:
                    datum_id = value[len(DATUM_URI_PREFIX):] if DATUM_URI_PREFIX in value else value
                    try:
                        UUID(str(datum_id))
                    except ValueError:
                        error(f"Not valid datum id: {value}")
                        return
                    endpoint_configurations[designated_endpoint]['files'][filename] = datum_id

        payload['endpoint_configurations'] = endpoint_configurations
        resp = request(
            method='post',
            url='/api/v0/deployment-versions/',
            json=payload,
        ).json()

        success(f"Deployment version {resp['name']} created. See {resp['urls']['display']}")
