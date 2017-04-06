import codecs
import os

import click

from valohai_cli.cli_utils import prompt_from_list
from valohai_cli.messages import error, success
from valohai_cli.utils import find_scripts

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

IMAGE_SUGGESTIONS = [
    {
        'name': 'gcr.io/tensorflow/tensorflow:1.0.1-devel-gpu-py3',
        'description': 'Tensorflow 1.0.1 with GPU support on Python 3',
    },
    {
        'name': 'gcr.io/tensorflow/tensorflow:1.0.1-devel-gpu',
        'description': 'Tensorflow 1.0.1 with GPU support on Python 2',
    },
    {
        'name': 'gcr.io/tensorflow/tensorflow:0.12.1-devel-gpu-py3',
        'description': 'Tensorflow 0.12.1 with GPU support on Python 3',
    },
    {
        'name': 'gcr.io/tensorflow/tensorflow:0.12.1-devel-gpu',
        'description': 'Tensorflow 0.12.1 with GPU support on Python 2',
    },
    {
        'name': 'valohai/keras:2.0.0-tensorflow1.0.1-python3.6-cuda8.0-cudnn5-devel-ubuntu16.04',
        'description': 'Keras 2.0.0 with TensorFlow 1.0.1 backend and GPU support on Python 3',
    },
    {
        'name': 'valohai/keras:2.0.0-theano0.9.0rc4-python3.6-cuda8.0-cudnn5-devel-ubuntu16.04',
        'description': 'Keras 2.0.0 with Theano 0.9.0rc4 backend and GPU support on Python 3',
    },
    {
        'name': 'valohai/keras:2.0.0-theano0.8.2-python3.6-cuda8.0-cudnn5-devel-ubuntu16.04',
        'description': 'Keras 2.0.0 with Theano 0.8.2 backend and GPU support on Python 3',
    },
    {
        'name': 'valohai/darknet:b61bcf5-cuda8.0-cudnn5-devel-ubuntu16.04',
        'description': 'Darknet with GPU support',
    },
]


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
            success('All done! Wrote {path}.'.format(path=yaml_path))
            break


def choose_image():
    click.echo(
        'Now let\'s pick a Docker image to use with your code.\n'
        'Here are some recommended choices, but feel free to type in one of your own.'
    )
    while True:
        image = prompt_from_list(
            IMAGE_SUGGESTIONS,
            'Choose a number or enter a Docker image name.',
            nonlist_validator=lambda s: s.strip()
        )
        if isinstance(image, dict):
            image = image['name']
        if click.confirm('Is {image} correct?'.format(image=click.style(image, bold=True))):
            break
    success('Great! Using {image}.'.format(image=image))
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
                    {'name': '{} {}'.format(interpreter, script)}
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
    success('Got it! Using {command} as the command.'.format(command=command))
    return command
