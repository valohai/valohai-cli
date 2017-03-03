# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from valohai_cli import __version__

setup(
    name='valohai-cli',
    version=__version__,
    entry_points={'console_scripts': ['vh=valohai_cli.cli:cli']},
    author='Valohai',
    author_email='hait@valohai.com',
    license='MIT',
    install_requires=[
        'click>=6.0',
        'six>=1.10.0',
        'valohai-yaml>=0.5',
        'requests[security]>=2.0.0',
    ],
    packages=find_packages(include=('valohai_cli*',)),
)
