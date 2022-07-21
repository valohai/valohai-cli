import collections
from typing import Any, Dict, Optional, Sequence, Set, Tuple

import click
from click import get_current_context
from click.core import Context, Option
from click.formatting import HelpFormatter
from valohai_yaml.objs import Step
from valohai_yaml.objs.input import Input
from valohai_yaml.objs.parameter import Parameter
from valohai_yaml.utils import listify

from valohai_cli.api import request
from valohai_cli.exceptions import CLIException
from valohai_cli.messages import success, warn
from valohai_cli.models.project import Project
from valohai_cli.utils import humanize_identifier, sanitize_option_name
from valohai_cli.utils.file_input import read_data_file
from valohai_cli.utils.friendly_option_parser import FriendlyOptionParser

from .excs import ExecutionCreationAPIError


def generate_sanitized_options(name: str) -> Set[str]:
    sanitized_name = sanitize_option_name(name)
    return {
        choice
        for choice in
        (
            f'--{sanitized_name}',
            f'--{sanitized_name}'.lower(),
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
        project: Project,
        step: Step,
        commit: str,
        environment: Optional[str] = None,
        image: Optional[str] = None,
        title: Optional[str] = None,
        watch: bool = False,
        download_directory: Optional[str] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        tags: Optional[Sequence[str]] = None,
        runtime_config: Optional[dict] = None,
    ):

        """
        Initialize the dynamic run command.

        :param environment_variables:
        :param project: Project object
        :param step: YAML step object
        :param commit: Commit identifier
        :param environment: Environment identifier (slug or UUID)
        :param environment_variables: Mapping of environment variables
        :param tags: Tags to apply
        :param watch: Whether to chain to `exec watch` afterwards
        :param image: Image override
        :param download_directory: Where to (if somewhere) to download execution outputs (sync mode)
        :param runtime_config: Runtime config dict
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
        self.runtime_config = dict(runtime_config or {})
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
            if name not in self.environment_variables and value.default is not None:
                self.environment_variables[name] = value.default

    def format_options(self, ctx: Context, formatter: HelpFormatter) -> None:
        opts_by_group = collections.defaultdict(list)
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                opts_by_group[getattr(param, 'help_group', None)].append(rv)

        for group_name, opts in sorted(opts_by_group.items(), key=lambda pair: (pair[0] or '')):
            with formatter.section(group_name or 'Options'):
                formatter.write_dl(opts)

    def convert_param_to_option(self, parameter: Parameter) -> Option:
        """
        Convert a Parameter into a click Option.
        """
        assert isinstance(parameter, Parameter)
        option = click.Option(
            param_decls=list(generate_sanitized_options(parameter.name)),
            required=False,  # This is done later
            default=parameter.default,
            help=parameter.description,
            type=self.parameter_type_map.get(parameter.type, click.STRING),
        )
        option.name = f'~{parameter.name}'  # Tildify so we can pick these out of kwargs easily
        option.help_group = 'Parameter Options'  # type: ignore[attr-defined]
        return option

    def convert_input_to_option(self, input: Input) -> Option:
        """
        Convert an Input into a click Option.
        """
        assert isinstance(input, Input)

        option = click.Option(
            param_decls=list(generate_sanitized_options(input.name)),
            required=(input.default is None and not input.optional),
            default=listify(input.default),
            metavar='URL',
            multiple=True,
            help=f'Input "{humanize_identifier(input.name)}"',
        )
        option.name = f'^{input.name}'  # Caretize so we can pick these out of kwargs easily
        option.help_group = 'Input Options'  # type: ignore[attr-defined]
        return option

    def execute(self, **kwargs: Any) -> None:
        """
        Execute the creation of the execution. (Heh.)

        This is the Click callback for this command.

        :param kwargs: Assorted kwargs (as passed in by Click).
        :return: Naught
        """
        options, parameters, inputs = self._sift_kwargs(kwargs)

        payload = {
            'commit': self.commit,
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
        if self.runtime_config:
            payload['runtime_config'] = self.runtime_config

        resp = request(
            method='post',
            url='/api/v0/executions/',
            json=payload,
            api_error_class=ExecutionCreationAPIError,
        ).json()
        success(f"Execution #{resp['counter']} created. See {resp['urls']['display']}")

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

    def _sift_kwargs(self, kwargs: Dict[str, str]) -> Tuple[dict, dict, dict]:
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

    def _process_parameters(self, parameters: Dict[str, Any], parameter_file: Optional[str]) -> None:
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

    def make_parser(self, ctx: Context) -> FriendlyOptionParser:
        parser: FriendlyOptionParser = super().make_parser(ctx)  # type: ignore[assignment]
        # This is somewhat naughty, but allows us to easily hook into here.
        # Besides, FriendlyOptionParser does inherit from OptionParser anyway,
        # and just overrides that one piece of behavior...
        parser.__class__ = FriendlyOptionParser
        return parser
