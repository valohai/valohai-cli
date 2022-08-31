import pytest
import yaml

from tests.commands.run_test_utils import ALTERNATIVE_YAML, RunAPIMock, RunTestSetup
from tests.fixture_data import CONFIG_YAML, PROJECT_DATA
from valohai_cli.commands.execution.run import run
from valohai_cli.ctx import get_project
from valohai_cli.models.project import Project

adhoc_mark = pytest.mark.parametrize('adhoc', (False, True), ids=('regular', 'adhoc'))


@pytest.fixture(params=['regular', 'adhoc'], ids=('regular', 'adhoc'))
def run_test_setup(request, logged_in_and_linked, monkeypatch):
    return RunTestSetup(monkeypatch=monkeypatch, adhoc=(request.param == 'adhoc'))


@pytest.fixture()
def patch_git(monkeypatch):
    def mock_resolve_commit(mock_self, *, commit_identifier):
        return {'identifier': commit_identifier}

    monkeypatch.setattr(Project, 'resolve_commit', mock_resolve_commit)


def test_run_requires_step(runner, logged_in_and_linked):
    assert 'Usage: run' in runner.invoke(run, catch_exceptions=False).output


@pytest.mark.parametrize('pass_env_var', ('custom', 'override-default'))
def test_run_env_var(run_test_setup, pass_env_var):
    run_test_setup.args.extend(['-v', 'greeting=hello'])
    run_test_setup.args.extend(['--var', 'enable=1'])
    run_test_setup.args.extend(['-vdebug=yes'])
    if pass_env_var == 'override-default':
        run_test_setup.args.extend(['--var', 'testenvvar='])
        expected_testenvvar = ''
    else:
        expected_testenvvar = 'test'  # default from YAML
    run_test_setup.values['environment_variables'] = {
        'greeting': 'hello',
        'enable': '1',
        'debug': 'yes',
        'testenvvar': expected_testenvvar,
    }
    run_test_setup.run()


def test_run_env(run_test_setup):
    run_test_setup.args.append('--environment=015dbd56-2670-b03e-f37c-dc342714f1b5')
    run_test_setup.values['environment'] = '015dbd56-2670-b03e-f37c-dc342714f1b5'
    run_test_setup.run()


def test_run_tags(run_test_setup):
    run_test_setup.args.extend(['--tag=bark', '--tag=bork', '--tag=vuh', '--tag=hau'])
    run_test_setup.values['tags'] = ['bark', 'bork', 'vuh', 'hau']
    run_test_setup.run()


def test_run_spot_restart(run_test_setup):
    run_test_setup.args.append('--autorestart-spot=True')
    run_test_setup.run()
    assert run_test_setup.run_api_mock.last_create_execution_payload["runtime_config"] == {
        'autorestart': True
    }


def test_run_with_yaml_path(run_test_setup):
    run_test_setup.args.remove('train')
    # Use a step which is only present in the evaluation YAML
    run_test_setup.args.append('batch feature extraction')
    run_test_setup.args.append(f'--yaml={ALTERNATIVE_YAML}')
    output = run_test_setup.run(verify_adhoc=run_test_setup.adhoc)
    # Adhoc success case already verified in `run()
    if not run_test_setup.adhoc:
        assert '--yaml can only be used with --adhoc' in output
    else:
        assert f'from configuration YAML at {ALTERNATIVE_YAML}' in output


def test_run_input(run_test_setup):
    run_test_setup.args.append('--in1=http://url')
    run_test_setup.args.append('--in1=http://anotherurl')
    run_test_setup.values['inputs'] = {'in1': ['http://url', 'http://anotherurl']}
    run_test_setup.run()


@pytest.mark.parametrize('pass_param', ('direct', 'file', 'mix'))
def test_run_params(tmpdir, run_test_setup, pass_param):
    values = {
        'parameters': {  # default from YAML
            'max_steps': 300,
            'learning_rate': 0.1337,
        },
    }
    if pass_param in ('direct', 'mix'):
        run_test_setup.args.append('--max-steps=1801')
        values['parameters']['max_steps'] = 1801

    if pass_param in ('file', 'mix'):
        params_yaml = tmpdir.join('params.yaml')
        params_yaml.write(yaml.safe_dump({'learning-rate': 1700}))
        run_test_setup.args.append(f'--parameter-file={params_yaml}')
        values['parameters']['learning_rate'] = 1700
    run_test_setup.values.update(values)
    run_test_setup.run()


def test_param_type_validation_integer(runner, logged_in_and_linked, patch_git, default_run_api_mock):
    with open(get_project().get_config_filename(), 'w') as yaml_fp:
        yaml_fp.write(CONFIG_YAML)
    rv = runner.invoke(run, ['train', '--max-steps=plonk'], catch_exceptions=False)
    assert (
        '\'plonk\' is not a valid integer' in rv.output or
        'plonk is not a valid integer' in rv.output
    )


def test_param_type_validation_flag(runner, logged_in_and_linked, patch_git, default_run_api_mock):
    with open(get_project().get_config_filename(), 'w') as yaml_fp:
        yaml_fp.write(CONFIG_YAML)
    rv = runner.invoke(run, ['train', '--enable-mega-boost=please'], catch_exceptions=False)
    assert (
        '\'please\' is not a valid boolean' in rv.output or
        'please is not a valid boolean' in rv.output
    )


@pytest.mark.parametrize('value, result', [
    # Various forms supported by `click.BOOL`...
    ('yes', True),
    ('no', False),
    ('1', True),
    ('FALSE', False),
    ('True', True),
])
def test_flag_param_coercion(tmpdir, run_test_setup, value, result):
    run_test_setup.values['parameters'] = {  # default from YAML
        'max_steps': 300,
        'learning_rate': 0.1337,
        'enable_mega_boost': result,
    }
    run_test_setup.args.append(f'--enable-mega-boost={value}')
    run_test_setup.run()


def test_run_no_git(runner, logged_in_and_linked):
    project_id = PROJECT_DATA['id']

    with open(get_project().get_config_filename(), 'w') as yaml_fp:
        yaml_fp.write(CONFIG_YAML)

    args = ['train']

    with RunAPIMock(project_id, 'f' * 16, {}):
        output = runner.invoke(run, args, catch_exceptions=False).output
        assert 'is not a Git repository' in output


def test_param_input_sanitization(runner, logged_in_and_linked, patch_git, default_run_api_mock):
    with open(get_project().get_config_filename(), 'w') as yaml_fp:
        yaml_fp.write('''
- step:
    name: Train model
    image: busybox
    command: "false"
    inputs:
      - name: Ridiculously Complex Input_Name
        default: http://example.com/
    parameters:
      - name: Parameter With Highly Convoluted Name
        pass-as: --simple={v}
        type: integer
        default: 1
''')
    output = runner.invoke(run, ['train', '--help'], catch_exceptions=False).output
    assert '--Parameter-With-Highly-Convoluted-Name' in output
    assert '--parameter-with-highly-convoluted-name' in output
    assert '--Ridiculously-Complex-Input-Name' in output
    assert '--ridiculously-complex-input-name' in output


def test_typo_check(runner, logged_in_and_linked, patch_git, default_run_api_mock):
    with open(get_project().get_config_filename(), 'w') as yaml_fp:
        yaml_fp.write(CONFIG_YAML)
    args = ['train', '--max-setps=80']  # Oopsy!
    output = runner.invoke(run, args, catch_exceptions=False).output
    assert '(Possible options:' in output or 'Did you mean' in output
    assert '--max-steps' in output


def test_run_help(runner, logged_in_and_linked):
    with open(get_project().get_config_filename(), 'w') as yaml_fp:
        yaml_fp.write(CONFIG_YAML)

    output = runner.invoke(run, ['--help'], catch_exceptions=False).output
    assert 'Train model' in output


def test_command_help(runner, logged_in_and_linked, patch_git, default_run_api_mock):
    with open(get_project().get_config_filename(), 'w') as yaml_fp:
        yaml_fp.write(CONFIG_YAML)

    output = runner.invoke(run, ['Train model', '--help'], catch_exceptions=False).output
    assert 'Parameter Options' in output
    assert 'Input Options' in output


def test_remote(run_test_setup, tmpdir):
    key = tmpdir.join("key.pub")
    key.write_text("ssh blarp blep", "utf-8")
    run_test_setup.args.append('--debug-port=8101')
    run_test_setup.args.append(f'--debug-key-file={key}')
    run_test_setup.run()
    assert run_test_setup.run_api_mock.last_create_execution_payload["runtime_config"] == {
        'debug_key': 'ssh blarp blep',
        'debug_port': 8101,
    }


def test_remote_both_args(run_test_setup):
    run_test_setup.args.append('--debug-port=8101')
    assert "Both or neither" in run_test_setup.run(catch_exceptions=False, verify_adhoc=False)
