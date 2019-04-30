import click

from valohai_cli.adhoc import create_adhoc_commit
from valohai_cli.ctx import get_project
from valohai_cli.messages import info
from valohai_cli.utils import parse_environment_variable_strings
from .dynamic_run_command import RunCommand
from .utils import match_step

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
@click.option('--adhoc', '-a', is_flag=True, help='Upload the current state of the working directory, then run it as an ad-hoc execution.')
@click.option( '--validate-adhoc/--no-validate-adhoc', help='Enable or disable validation of adhoc packaged code, on by default', default=True)
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx, step, commit, environment, watch, sync, title, adhoc, image, environment_variables, validate_adhoc, args):
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

    if adhoc:
        if commit:
            raise click.UsageError('--commit and --adhoc are mutually exclusive.')
        if project.is_remote:
            raise click.UsageError('--adhoc can not be used with remote projects.')

    if sync and watch:
        raise click.UsageError('Combining --sync and --watch not supported yet.')

    if not commit and project.is_remote:
        # For remote projects, we need to resolve early.
        commit = project.resolve_commit()['identifier']
        info('Using remote project {name}\'s newest commit {commit}'.format(
            name=project.name,
            commit=commit,
        ))

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
            rc.commit = create_adhoc_commit(project, validate=validate_adhoc)['identifier']
        return rc.invoke(child_ctx)
