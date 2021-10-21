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
        'gitignorant>=0.1.2',
        'requests-toolbelt>=0.7.1',
        'requests>=2.0.0',
        'typing-extensions>=3.7',
        'valohai-utils>=0.1.10',
        'valohai-yaml>=0.15.0',
    ],
    python_requires='>=3.6',
    packages=find_packages(include=('valohai_cli*',)),
    include_package_data=True,
)
