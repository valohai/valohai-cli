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
from valohai_cli.exceptions import NoGitRepo
from valohai_cli.utils.friendly_option_parser import FriendlyOptionParser
from valohai_cli.messages import success, warn, info
from valohai_cli.utils import (
    humanize_identifier,
    match_prefix,
    sanitize_option_name,
    parse_environment_variable_strings,
)


def generate_sanitized_options(name):
    sanitized_name = sanitize_option_name(name)
    return set(choice for choice in (
        '--%s' % sanitized_name,
        ('--%s' % sanitized_name).lower(),
    ) if ' ' not in choice)


class RunCommand(click.Command):
    """
    A dynamically-generated subcommand that has Click options for parameters and inputs.
    """
    parameter_type_map = {
        'integer': click.INT,
        'float': click.FLOAT,
    }

    def __init__(self,
        project,
        step,
        commit,
        environment=None,
        image=None,
        title=None,
        watch=False,
        sync=None,
        environment_variables=None,
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
        self.sync = sync
        self.title = title
        self.environment_variables = dict(environment_variables or {})
        super(RunCommand, self).__init__(
            name=sanitize_option_name(step.name.lower()),
            callback=self.execute,
            epilog='Multiple files per input: --my-input=myurl --my-input=myotherurl',
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
            default=([input.default] if input.default else []),
            metavar='URL',
            multiple=True,
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
        if self.environment_variables:
            payload['environment_variables'] = self.environment_variables

        resp = request('post', '/api/v0/executions/', json=payload).json()
        success('Execution #{counter} created. See {link}'.format(
            counter=resp['counter'],
            link=resp['urls']['display'],
        ))

        ctx = get_current_context()

        if self.sync:
            from valohai_cli.commands.execution.outputs import outputs
            ctx.invoke(outputs, counter=resp['counter'], download=self.sync, sync=True)

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
        return (options, params, inputs)

    def resolve_commit(self, commit_identifier):
        if not commit_identifier:
            try:
                commit_identifier = git.get_current_commit(self.project.directory)
            except NoGitRepo as exc:
                warn(
                    'The directory is not a Git repository. \n'
                    'Would you like to just run using the latest commit known by Valohai?'
                )
                if not click.confirm('Use latest commit?', default=True):
                    raise click.Abort()

        try:
            commit_obj = self.project.resolve_commit(commit_identifier=commit_identifier)
        except KeyError:
            warn('Commit {commit} is not known for the project. Have you pushed it?'.format(commit=commit_identifier))
            raise click.Abort()
        except IndexError:
            warn('No commits are known for the project.')
            raise click.Abort()

        resolved_commit_identifier = commit_obj['identifier']
        if not commit_identifier:
            click.echo('Resolved to commit {commit}'.format(commit=resolved_commit_identifier))

        return resolved_commit_identifier

    def make_parser(self, ctx):
        parser = super(RunCommand, self).make_parser(ctx)
        # This is somewhat naughty, but allows us to easily hook into here.
        # Besides, FriendlyOptionParser does inherit from OptionParser anyway,
        # and just overrides that one piece of behavior...
        parser.__class__ = FriendlyOptionParser
        return parser


run_epilog = (
    'More detailed help (e.g. how to define parameters and inputs) is available when you have '
    'defined which step to run. For instance, if you have a step called Extract, '
    'try running `vh exec run Extract --help`.'
)


@click.command(
    context_settings=dict(ignore_unknown_options=True),
    add_help_option=False,
    epilog=run_epilog,
)
@click.argument('step')
@click.option('--commit', '-c', default=None, metavar='SHA', help='The commit to use. Defaults to the current HEAD.')
@click.option('--environment', '-e', default=None, help='The environment UUID or slug to use (see `vh env`)')
@click.option('--image', '-i', default=None, help='Override the Docker image specified in the step.')
@click.option('--title', '-t', default=None, help='Title of the execution.')
@click.option('--watch', '-w', is_flag=True, help='Start `exec watch`ing the execution after it starts.')
@click.option('--var', '-v', 'environment_variables', multiple=True, help='Add environment variable (NAME=VALUE). May be repeated.')
@click.option('--sync', '-s', type=click.Path(file_okay=False), help='Download execution outputs to DIRECTORY.', default=None)

@click.option(
    '--adhoc',
    '-a',
    is_flag=True,
    help='Upload the current state of the working directory, then run it as an ad-hoc execution.')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx, step, commit, environment, watch, sync, title, adhoc, image, environment_variables, args):
    """
    Start an execution of a step.
    """
    if step == '--help':  # This is slightly weird, but it's because of the nested command thing
        click.echo(ctx.get_help(), color=ctx.color)
        try:
            config = get_project(require=True).get_config(commit_identifier=commit)
            if config.steps:
                click.echo('\nThese steps are available in the selected commit:\n', color=ctx.color)
                for step in sorted(config.steps):
                    click.echo('   * %s' % step, color=ctx.color)
        except:  # If we fail to extract the step list, it's not that big of a deal.
            pass
        ctx.exit()
    project = get_project(require=True)

    if adhoc and commit:
        raise click.UsageError('--commit and --adhoc are mutually exclusive.')
    if sync and watch:
        raise click.UsageError('Combining --sync and --watch not supported yet.')

    # We need to pass commit=None when adhoc=True to `get_config`, but
    # the further steps do need the real commit identifier from remote,
    # so this is done before `commit` is mangled by `create_adhoc_commit`.
    config = project.get_config(commit_identifier=commit)
    matched_step = match_step(config, step)
    step = config.steps[matched_step]

    rc = RunCommand(
        project=project,
        step=step,
        commit=commit,
        environment=environment,
        watch=watch,
        sync=sync,
        image=image,
        title=title,
        environment_variables=parse_environment_variable_strings(environment_variables),
    )
    with rc.make_context(rc.name, list(args), parent=ctx) as child_ctx:
        if adhoc:
            rc.commit = create_adhoc_commit(project)['identifier']
        return rc.invoke(child_ctx)


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
