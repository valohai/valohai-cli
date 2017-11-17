import os

import six
import valohai_yaml
from valohai_yaml import ValidationErrors

from valohai_cli.api import request
from valohai_cli.exceptions import InvalidConfig, NoExecution, APIError


class Project:

    def __init__(self, data, directory=None):
        self.data = data
        self.directory = directory

    id = property(lambda p: p.data['id'])
    name = property(lambda p: p.data['name'])

    def get_config(self):
        filename = self.get_config_filename()
        try:
            with open(filename) as infp:
                config = valohai_yaml.parse(infp)
                config.project = self
                return config
        except IOError as ioe:
            six.raise_from(InvalidConfig('Could not read %s' % filename), ioe)
        except ValidationErrors as ves:
            raise InvalidConfig('{filename} is invalid ({n} errors); see `vh lint`'.format(
                filename=filename,
                n=len(ves.errors),
            ))

    def get_config_filename(self):
        return os.path.join(self.directory, 'valohai.yaml')

    def get_execution_from_counter(self, counter):
        try:
            return request(
                'get',
                '/api/v0/executions/{project_id}:{counter}/'.format(project_id=self.id, counter=counter),
            ).json()
        except APIError as ae:
            if ae.response.status_code == 404:
                raise NoExecution('Execution #{counter} does not exist'.format(counter=counter))
            raise

    def __str__(self):
        return self.name
