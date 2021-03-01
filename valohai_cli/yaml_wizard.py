import codecs
import os

import click
import requests
import yaml

from valohai_cli.messages import error, success, warn
from valohai_cli.utils import find_scripts
from valohai_cli.utils.cli_utils import prompt_from_list

YAML_SKELLINGTON = """---

- step:
    name: Execute {command}
    image: {image}
    command: {command}
    #inputs:
    #  - name: example-input
    #    default: https://example.com/
    #parameters:
    # - name: example
    #   description: Example parameter
    #   type: integer
    #   default: 300
"""


def get_image_suggestions():
    try:
        resp = requests.get('https://raw.githubusercontent.com/valohai/images/master/images.yaml')
        resp.raise_for_status()
        data = yaml.safe_load(resp.content)
        description_map = data.get('descriptions', {})
        return [
            {
                'name': image,
                'description': description_map.get(image),
            }
            for image
            in data.get('suggestions', [])
        ]
    except Exception as exc:
        warn(f'Could not load online image suggestions: {exc}')
        return []


def yaml_wizard(directory):
    while True:
        command = choose_command(directory)
        image = choose_image()
        yaml = YAML_SKELLINGTON.format(
            image=image,
            command=command,
        )
        click.secho('Here\'s a preview of the Valohai.yaml file I\'m going to create.', fg='cyan')
        print(yaml)
        yaml_path = os.path.join(directory, 'valohai.yaml')
        if not click.confirm('Write this to {path}?'.format(path=click.style(yaml_path, bold=True))):  # pragma: no cover
            click.echo('Okay, let\'s try again...')
            continue
        with codecs.open(yaml_path, 'w', 'UTF-8') as out_fp:
            out_fp.write(yaml)
            success(f'All done! Wrote {yaml_path}.')
            break


def choose_image():
    image_suggestions = get_image_suggestions()
    click.echo(
        'Now let\'s pick a Docker image to use with your code.\n' +
        (
            'Here are some recommended choices, but feel free to type in one of '
            'your own from the ones available at https://hub.docker.com/'
            if image_suggestions
            else ''
        )
    )
    while True:
        image = prompt_from_list(
            image_suggestions,
            (
                'Choose a number or enter a Docker image name.'
                if image_suggestions else
                'Enter a Docker image name.'
            ),
            nonlist_validator=lambda s: s.strip()
        )
        if isinstance(image, dict):
            image = image['name']
        if click.confirm('Is {image} correct?'.format(image=click.style(image, bold=True))):
            break
    success(f'Great! Using {image}.')
    return image


def choose_command(directory):
    scripts = sorted(find_scripts(directory))
    while True:
        if scripts:
            click.echo(
                'We found these script files in this directory.\n'
                'If any of them is the script file you\'d like to use for Valohai, type its number.\n'
                'Otherwise, you can just type the command to run.'
            )
            command = prompt_from_list(
                [
                    {'name': f'{interpreter} {script}'}
                    for (interpreter, script)
                    in scripts
                ],
                'Choose a number or enter a command.',
                nonlist_validator=lambda s: s.strip()
            )
            if isinstance(command, dict):
                command = command['name']
        else:  # pragma: no cover
            command = click.prompt(
                'We couldn\'t find script files in this directory.\n'
                'Please enter the command you\'d like to run in the Valohai platform.\n'
            )
        if not command:  # pragma: no cover
            error('Please try again.')
            continue
        if click.confirm('Is {command} correct?'.format(command=click.style(command, bold=True))):
            break
    success(f'Got it! Using {command} as the command.')
    return command
