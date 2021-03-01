import collections

import click
from click import get_current_context
from valohai_yaml.objs import Parameter, Step
from valohai_yaml.objs.input import Input

from valohai_cli import git as git
from valohai_cli.api import request
from valohai_cli.exceptions import CLIException, NoGitRepo
from valohai_cli.messages import success, warn
from valohai_cli.utils import humanize_identifier, sanitize_option_name
from valohai_cli.utils.file_input import read_data_file
from valohai_cli.utils.friendly_option_parser import FriendlyOptionParser

from .excs import ExecutionCreationAPIError


def generate_sanitized_options(name):
    sanitized_name = sanitize_option_name(name)
    return {
        choice
        for choice in
        (
            '--%s' % sanitized_name,
            ('--%s' % sanitized_name).lower(),
        )
        if ' ' not in choice
    }


class RunCommand(click.Command):
    """
    A dynamically-generated subcommand that has Click options for parameters and inputs.
    """
    parameter_type_map = {
        'integer': click.INT,
        'float': click.FLOAT,
        'flag': click.BOOL,
    }

    def __init__(
        self,
        project,
        step,
        commit,
        environment=None,
        image=None,
        title=None,
        watch=False,
        download_directory=None,
        environment_variables=None,
        tags=None
    ):

        """
        Initialize the dynamic run command.

        :param environment_variables:
        :param project: Project object
        :type project: valohai_cli.models.project.Project
        :param step: YAML step object
        :type step: valohai_yaml.objs.Step
        :param commit: Commit identifier
        :type commit: str
        :param environment: Environment identifier (slug or UUID)
        :type environment: str|None
        :param environment_variables: Mapping of environment variables
        :type environment_variables: dict[str, str]|None
        :param tags: Tags to apply
        :type tags: list[str]
        :param watch: Whether to chain to `exec watch` afterwards
        :type watch: bool
        :param image: Image override
        :type image: str|None
        :param download_directory: Where to (if somewhere) to download execution outputs (sync mode)
        :param download_directory: str|None
        """
        assert isinstance(step, Step)
        self.project = project
        self.step = step
        self.commit = commit
        self.environment = environment
        self.image = image
        self.watch = bool(watch)
        self.download_directory = download_directory
        self.title = title
        self.environment_variables = dict(environment_variables or {})
        self.tags = list(tags or [])
        super().__init__(
            name=sanitize_option_name(step.name.lower()),
            callback=self.execute,
            epilog='Multiple files per input: --my-input=myurl --my-input=myotherurl',
            add_help_option=True,
        )
        self.params.append(click.Option(
            ['--parameter-file'],
            type=click.Path(exists=True, dir_okay=False),
            help='Read parameter values from JSON/YAML file',
        ))
        for parameter in step.parameters.values():
            self.params.append(self.convert_param_to_option(parameter))
        for input in step.inputs.values():
            self.params.append(self.convert_input_to_option(input))
        for name, value in step.environment_variables.items():
            if name not in self.environment_variables:
                self.environment_variables[name] = value.default

    def format_options(self, ctx, formatter):
        opts_by_group = collections.defaultdict(list)
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                opts_by_group[getattr(param, 'help_group', None)].append(rv)

        for group_name, opts in sorted(opts_by_group.items(), key=lambda pair: (pair[0] or '')):
            with formatter.section(group_name or 'Options'):
                formatter.write_dl(opts)

    def convert_param_to_option(self, parameter):
        """
        Convert a Parameter into a click Option.

        :type parameter: valohai_yaml.objs.Parameter
        :rtype: click.Option
        """
        assert isinstance(parameter, Parameter)
        option = click.Option(
            param_decls=list(generate_sanitized_options(parameter.name)),
            required=False,  # This is done later
            default=parameter.default,
            help=parameter.description,
            type=self.parameter_type_map.get(parameter.type, click.STRING),
        )
        option.name = '~%s' % parameter.name  # Tildify so we can pick these out of kwargs easily
        option.help_group = 'Parameter Options'
        return option

    def convert_input_to_option(self, input):
        """
        Convert an Input into a click Option.

        :type input: valohai_yaml.objs.input.Input
        :rtype: click.Option
        """
        assert isinstance(input, Input)
        default_as_list = input.default if isinstance(input.default, list) else [input.default]

        option = click.Option(
            param_decls=list(generate_sanitized_options(input.name)),
            required=(input.default is None and not input.optional),
            default=(default_as_list if input.default else []),
            metavar='URL',
            multiple=True,
            help='Input "%s"' % humanize_identifier(input.name),
        )
        option.help_group = 'Input Options'
        option.name = '^%s' % input.name  # Caretize so we can pick these out of kwargs easily
        return option

    def execute(self, **kwargs):
        """
        Execute the creation of the execution. (Heh.)

        This is the Click callback for this command.

        :param kwargs: Assorted kwargs (as passed in by Click).
        :return: Naught
        """
        options, parameters, inputs = self._sift_kwargs(kwargs)
        commit = self.resolve_commit(self.commit)

        payload = {
            'commit': commit,
            'inputs': inputs,
            'parameters': parameters,
            'project': self.project.id,
            'step': self.step.name,
        }
        if self.environment:
            payload['environment'] = self.environment
        if self.image:
            payload['image'] = self.image
        if self.title:
            payload['title'] = self.title
        if self.environment_variables:
            payload['environment_variables'] = self.environment_variables
        if self.tags:
            payload['tags'] = self.tags

        resp = request(
            method='post',
            url='/api/v0/executions/',
            json=payload,
            api_error_class=ExecutionCreationAPIError,
        ).json()
        success('Execution #{counter} created. See {link}'.format(
            counter=resp['counter'],
            link=resp['urls']['display'],
        ))

        ctx = get_current_context()

        if self.download_directory:
            from valohai_cli.commands.execution.outputs import outputs as outputs_command
            ctx.invoke(
                outputs_command,
                counter=resp['counter'],
                sync=True,
                download_directory=self.download_directory,
            )

        if self.watch:
            from valohai_cli.commands.execution.watch import watch
            ctx.invoke(watch, counter=resp['counter'])

    def _sift_kwargs(self, kwargs):
        # Sift kwargs into params, options, and inputs
        options = {}
        params = {}
        inputs = {}
        for key, value in kwargs.items():
            if key.startswith('~'):
                params[key[1:]] = value
            elif key.startswith('^'):
                inputs[key[1:]] = value
            else:
                options[key] = value
        self._process_parameters(params, parameter_file=options.get('parameter_file'))
        return (options, params, inputs)

    def _process_parameters(self, parameters, parameter_file):
        if parameter_file:
            parameter_file_data = read_data_file(parameter_file)
            if not isinstance(parameter_file_data, dict):
                raise CLIException('Parameter file could not be parsed as a dictionary')

            for name, parameter in self.step.parameters.items():
                # See if we can match the name or the sanitized name to an option
                for key in (name, sanitize_option_name(name)):
                    if key not in parameter_file_data:
                        continue
                    value = parameter_file_data.pop(key)
                    type = self.parameter_type_map.get(parameter.type, click.STRING)
                    value = type.convert(value, param=None, ctx=None)
                    parameters[name] = value

            if parameter_file_data:  # Not everything was popped off
                unparsed_parameter_names = ', '.join(sorted(str(k) for k in parameter_file_data))
                warn(f'Parameters ignored in parameter file: {unparsed_parameter_names}')

        missing_required_parameters = set()
        for name, parameter in self.step.parameters.items():
            if name in parameters:
                # Clean out default-less flag parameters whose value would be None
                if parameter.type == 'flag' and parameters[name] is None:
                    del parameters[name]
            else:
                required = (parameter.default is None and not parameter.optional)
                if required:
                    missing_required_parameters.add(name)
        if missing_required_parameters:
            raise CLIException(f'Required parameters missing: {missing_required_parameters}')

    def resolve_commit(self, commit_identifier):
        if not commit_identifier:
            try:
                commit_identifier = git.get_current_commit(self.project.directory)
            except NoGitRepo:
                warn(
                    'The directory is not a Git repository. \n'
                    'Would you like to just run using the latest commit known by Valohai?'
                )
                if not click.confirm('Use latest commit?', default=True):
                    raise click.Abort()

        if commit_identifier and commit_identifier.startswith('~'):
            # Assume ad-hoc commits are qualified already
            return commit_identifier

        try:
            commit_obj = self.project.resolve_commit(commit_identifier=commit_identifier)
        except KeyError:
            warn(f'Commit {commit_identifier} is not known for the project. Have you pushed it?')
            raise click.Abort()
        except IndexError:
            warn('No commits are known for the project.')
            raise click.Abort()

        resolved_commit_identifier = commit_obj['identifier']
        if not commit_identifier:
            click.echo(f'Resolved to commit {resolved_commit_identifier}', err=True)

        return resolved_commit_identifier

    def make_parser(self, ctx):
        parser = super().make_parser(ctx)
        # This is somewhat naughty, but allows us to easily hook into here.
        # Besides, FriendlyOptionParser does inherit from OptionParser anyway,
        # and just overrides that one piece of behavior...
        parser.__class__ = FriendlyOptionParser
        return parser
