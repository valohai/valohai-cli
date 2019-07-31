# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

from valohai_cli import __version__

setup(
    name='valohai-cli',
    version=__version__,
    entry_points={'console_scripts': ['vh=valohai_cli.cli:cli']},
    author='Valohai',
    author_email='hait@valohai.com',
    license='MIT',
    install_requires=[
        'click>=7.0',
        'six>=1.10.0',
        'valohai-yaml>=0.9',
        'requests[security]>=2.0.0',
        'requests-toolbelt>=0.7.1',
    ],
    packages=find_packages(include=('valohai_cli*',)),
)
