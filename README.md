# Valohai Command Line Client

![CircleCI](https://img.shields.io/circleci/project/github/valohai/valohai-cli.svg)
![Codecov](https://img.shields.io/codecov/c/github/valohai/valohai-cli.svg)
![PyPI](https://img.shields.io/pypi/v/valohai-cli.svg)
![MIT License](https://img.shields.io/github/license/valohai/valohai-cli.svg)

This is the command-line client for the [Valohai][vh] machine learning IaaS platform.

Installation
------------

`valohai-cli` supports Python 3.6 and higher.

If you still need to run on Python 3.5, version 0.13.0 was the last one to support it.

The easiest way to get started is to install `valohai-cli` system-wide with `pip`.

```bash
$ pip3 install -U valohai-cli
```

The `-U` flag ensures that any present version is upgraded, too.

After you've installed the client, `vh` should work and you should see a description
of commands.

> If you want to keep your global Python package environment clean,
we recommend installing `valohai-cli` in a virtualenv.  You can still access the command
from anywhere on your system by creating a symlink or alias to the `bin/vh` file.

Getting Started
---------------

See the [tutorial document](./TUTORIAL.md)!

[vh]: https://valohai.com/
[app]: https://app.valohai.com/

Developing
----------

To work on the `valohai-cli` code: pull the repository, create and activate a virtualenv, then run

```
pip install -e .
```

(The `-e` stands for `--editable`.)

This makes a new `vh` command available in the virtualenv, but linked to the working copy's
source.  That is, you can now edit the source under `valohai_cli` in your working directory,
and try it out with `vh`.
