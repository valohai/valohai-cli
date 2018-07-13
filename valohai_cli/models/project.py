import os

import six
import valohai_yaml
from click import BadParameter

from valohai_cli.api import request
from valohai_cli.exceptions import InvalidConfig, NoExecution, APIError
from valohai_cli.git import get_file_at_commit


class Project:

    def __init__(self, data, directory=None):
        self.data = data
        self.directory = directory

    id = property(lambda p: p.data['id'])
    name = property(lambda p: p.data['name'])

    def get_config(self, commit=None):
        """
        Get the `valohai_yaml.Config` object from the current working directory,
        or a given commit.

        :param commit: Hexadecimal commit identifier; optional.
        :type commit: str|None
        :return: valohai_yaml.Config
        :rtype: valohai_yaml.Config
        """
        if not commit:  # Current working directory
            filename = self.get_config_filename()
            with open(filename, 'r') as infp:
                return self._parse_config(infp, filename)
        else:  # Arbitrary commit
            filename = '{}:valohai.yaml'.format(commit)
            config_bytes = get_file_at_commit(self.directory, commit, 'valohai.yaml')
            config_sio = six.StringIO(config_bytes.decode('utf-8'))
            return self._parse_config(config_sio, filename)

    def _parse_config(self, config_fp, filename='<config file>'):
        try:
            config = valohai_yaml.parse(config_fp)
            config.project = self
            return config
        except IOError as ioe:
            six.raise_from(InvalidConfig('Could not read %s' % filename), ioe)
        except valohai_yaml.ValidationErrors as ves:
            raise InvalidConfig('{filename} is invalid ({n} errors); see `vh lint`'.format(
                filename=filename,
                n=len(ves.errors),
            ))

    def get_config_filename(self):
        return os.path.join(self.directory, 'valohai.yaml')

    def get_execution_from_counter(self, counter, params=None):
        if isinstance(counter, str):
            counter = counter.lstrip('#')
            if not (counter.isdigit() or counter == 'latest'):
                raise BadParameter(
                    '{counter} is not a valid counter value; it must be an integer or "latest"'.format(counter=counter),
                )
        try:
            return request(
                method='get',
                url='/api/v0/executions/{project_id}:{counter}/'.format(project_id=self.id, counter=counter),
                params=(params or {}),
            ).json()
        except APIError as ae:
            if ae.response.status_code == 404:
                raise NoExecution('Execution #{counter} does not exist'.format(counter=counter))
            raise

    def __str__(self):
        return self.name
