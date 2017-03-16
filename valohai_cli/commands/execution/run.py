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
from valohai_cli.messages import success, warn
from valohai_cli.utils import humanize_identifier, match_prefix


# TODO: this should use the step config from an overridden commit

class RunCommand(click.Command):
    """
    A dynamically-generated subcommand that has Click options for parameters and inputs.
    """
    parameter_type_map = {
        'integer': click.INT,
        'float': click.FLOAT,
    }

    def __init__(self, project, step, commit, environment, watch):
        """
        Initialize the dynamic run command.

        :param project: Project object
        :type project: valohai_cli.models.project.Project
        :param step: YAML step object
        :type step: valohai_yaml.objs.Step
        :param commit: Commit identifier
        :type commit: str
        :param environment: Environment name
        :type environment: str
        :param watch: Whether to chain to `exec watch` afterwards
        :type watch: bool
        """
        assert isinstance(step, Step)
        self.project = project
        self.step = step
        self.commit = commit
        self.environment = environment
        self.watch = bool(watch)
        super(RunCommand, self).__init__(
            name=step.name.lower().replace(' ', '-'),
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
            param_decls=[
                '--%s' % parameter.name.replace('_', '-'),
            ],
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
            param_decls=[
                '--%s' % input.name.replace('_', '-'),
            ],
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


@click.command(context_settings=dict(ignore_unknown_options=True), add_help_option=False)
@click.argument('step')
@click.option('--commit', '-c', default=None, metavar='SHA', help='The commit to use. Defaults to the current HEAD.')
@click.option('--environment/--env', '-e', default=None, help='The environment name/ID to use.')
@click.option('--watch', '-w', is_flag=True, help='Start `exec watch`ing the execution after it starts')
@click.option(
    '--adhoc',
    '-a',
    is_flag=True,
    help='Upload the current state of the working directory, then run it as an ad-hoc execution')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx, step, commit, environment, watch, adhoc, args):
    """
    Start an execution of a step.
    """
    if step == '--help':  # This is slightly weird, but it's because of the nested command thing
        click.echo(ctx.get_help(), color=ctx.color)
        ctx.exit()
    project = get_project(require=True)
    if adhoc:
        commit = create_adhoc_commit(project)['identifier']
    config = project.get_config()
    step = match_prefix(config.steps, step)
    if not step:
        raise BadParameter(
            '{step} is not a known step (try one of {steps})'.format(
                step=step,
                steps=', '.join(click.style(t, bold=True) for t in sorted(config.steps))
            ))
    step = config.steps[step]
    rc = RunCommand(project, step, commit=commit, environment=environment, watch=watch)
    with rc.make_context(rc.name, list(args), parent=ctx) as ctx:
        return rc.invoke(ctx)
