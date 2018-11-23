import re

import click
from click.exceptions import BadParameter
from click.globals import get_current_context
from valohai_yaml.objs.input import Input
from valohai_yaml.objs.parameter import Parameter
from valohai_yaml.objs.step import Step

import valohai_cli.git as git  # this import style required for tests
from valohai_cli.adhoc import create_adhoc_commit
from valohai_cli.api import request
from valohai_cli.ctx import get_project
from valohai_cli.utils.friendly_option_parser import FriendlyOptionParser
from valohai_cli.messages import success, warn
from valohai_cli.utils import humanize_identifier, match_prefix


def sanitize_name(name):
    return re.sub(r'[_ ]', '-', name)


def generate_sanitized_options(name):
    seen = set()
    for choice in (
        '--%s' % name,
        '--%s' % sanitize_name(name),
        ('--%s' % sanitize_name(name)).lower(),
    ):
        if ' ' in choice:
            continue
        if choice not in seen:
            seen.add(choice)
            yield choice


class RunCommand(click.Command):
    """
    A dynamically-generated subcommand that has Click options for parameters and inputs.
    """
    parameter_type_map = {
        'integer': click.INT,
        'float': click.FLOAT,
    }

    def __init__(self, project, step, commit, environment, image, title, watch):
        """
        Initialize the dynamic run command.

        :param project: Project object
        :type project: valohai_cli.models.project.Project
        :param step: YAML step object
        :type step: valohai_yaml.objs.Step
        :param commit: Commit identifier
        :type commit: str
        :param environment: Environment identifier (slug or UUID)
        :type environment: str
        :param watch: Whether to chain to `exec watch` afterwards
        :type watch: bool
        :param image: Image override
        :type image: str|None
        """
        assert isinstance(step, Step)
        self.project = project
        self.step = step
        self.commit = commit
        self.environment = environment
        self.image = image
        self.watch = bool(watch)
        self.title = title
        super(RunCommand, self).__init__(
            name=sanitize_name(step.name.lower()),
            callback=self.execute,
            add_help_option=True,
        )
        for parameter in step.parameters.values():
            self.params.append(self.convert_param_to_option(parameter))
        for input in step.inputs.values():
            self.params.append(self.convert_input_to_option(input))

    def convert_param_to_option(self, parameter):
        """
        Convert a Parameter into a click Option.

        :type parameter: valohai_yaml.objs.Parameter
        :rtype: click.Option
        """
        assert isinstance(parameter, Parameter)
        option = click.Option(
            param_decls=list(generate_sanitized_options(parameter.name)),
            required=(parameter.default is None and not parameter.optional),
            default=parameter.default,
            help=parameter.description,
            type=self.parameter_type_map.get(parameter.type, click.STRING),
        )
        option.name = '~%s' % parameter.name  # Tildify so we can pick these out of kwargs easily
        return option

    def convert_input_to_option(self, input):
        """
        Convert an Input into a click Option.

        :type input: valohai_yaml.objs.input.Input
        :rtype: click.Option
        """
        assert isinstance(input, Input)
        option = click.Option(
            param_decls=list(generate_sanitized_options(input.name)),
            required=(input.default is None and not input.optional),
            default=input.default,
            metavar='URL',
            help='Input "%s"' % humanize_identifier(input.name),
        )
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

        resp = request('post', '/api/v0/executions/', json=payload).json()
        success('Execution #{counter} created. See {link}'.format(
            counter=resp['counter'],
            link=resp['urls']['display'],
        ))
        if self.watch:
            ctx = get_current_context()
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
        return (options, params, inputs)

    def resolve_commit(self, commit):
        if not commit:
            commit = git.get_current_commit(self.project.directory)

        commits = request('get', '/api/v0/projects/{id}/commits/'.format(id=self.project.id)).json()
        by_identifier = {c['identifier']: c for c in commits}
        if commit not in by_identifier:
            warn('Commit {commit} is not known for the project. Have you pushed it?'.format(commit=commit))
            raise click.Abort()

        return commit

    def make_parser(self, ctx):
        parser = super(RunCommand, self).make_parser(ctx)
        # This is somewhat naughty, but allows us to easily hook into here.
        # Besides, FriendlyOptionParser does inherit from OptionParser anyway,
        # and just overrides that one piece of behavior...
        parser.__class__ = FriendlyOptionParser
        return parser


@click.command(context_settings=dict(ignore_unknown_options=True), add_help_option=False)
@click.argument('step')
@click.option('--commit', '-c', default=None, metavar='SHA', help='The commit to use. Defaults to the current HEAD.')
@click.option('--environment', '-e', default=None, help='The environment UUID or slug to use.')
@click.option('--image', '-i', default=None, help='Override the Docker image specified in the step')
@click.option('--title', '-t', default=None, help='Title of the execution.')
@click.option('--watch', '-w', is_flag=True, help='Start `exec watch`ing the execution after it starts')
@click.option(
    '--adhoc',
    '-a',
    is_flag=True,
    help='Upload the current state of the working directory, then run it as an ad-hoc execution')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx, step, commit, environment, watch, title, adhoc, image, args):
    """
    Start an execution of a step.
    """
    if step == '--help':  # This is slightly weird, but it's because of the nested command thing
        click.echo(ctx.get_help(), color=ctx.color)
        ctx.exit()
    project = get_project(require=True)

    if adhoc and commit:
        raise click.UsageError('--commit and --adhoc are mutually exclusive.')

    # We need to pass commit=None when adhoc=True to `get_config`, but
    # the further steps do need the real commit identifier from remote,
    # so this is done before `commit` is mangled by `create_adhoc_commit`.
    config = project.get_config(commit=commit)
    matched_step = match_step(config, step)
    step = config.steps[matched_step]

    if adhoc:
        commit = create_adhoc_commit(project)['identifier']

    rc = RunCommand(project, step, commit=commit, environment=environment, watch=watch, image=image, title=title)
    with rc.make_context(rc.name, list(args), parent=ctx) as ctx:
        return rc.invoke(ctx)


def match_step(config, step):
    if step in config.steps:
        return step
    step_matches = match_prefix(config.steps, step, return_unique=False)
    if not step_matches:
        raise BadParameter(
            '"{step}" is not a known step (try one of {steps})'.format(
                step=step,
                steps=', '.join(click.style(t, bold=True) for t in sorted(config.steps))
            ), param_hint='step')
    if len(step_matches) > 1:
        raise BadParameter(
            '"{step}" is ambiguous.\nIt matches {matches}.\nKnown steps are {steps}.'.format(
                step=step,
                matches=', '.join(click.style(t, bold=True) for t in sorted(step_matches)),
                steps=', '.join(click.style(t, bold=True) for t in sorted(config.steps)),
            ), param_hint='step')
    return step_matches[0]
