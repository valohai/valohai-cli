# Valohai Command Line Client

![CI](https://img.shields.io/github/actions/workflow/status/valohai/valohai-cli/ci.yml?branch=master)
![Codecov](https://img.shields.io/codecov/c/github/valohai/valohai-cli.svg)
![PyPI](https://img.shields.io/pypi/v/valohai-cli.svg)
![MIT License](https://img.shields.io/github/license/valohai/valohai-cli.svg)

This is the command-line client for the [Valohai][vh] machine learning IaaS platform.

## Installation

`valohai-cli` supports Python 3.7 and higher.

If you still need to run on Python 3.5, version 0.13.0 was the last one to support it.
If you still need to run on Python 3.6, version 0.23.0 was the last one to support it.

### System-wide or user-wide installation with pipx

The recommended way to install `valohai-cli` system-wide is to use [`pipx`][pipx], an
utility to install and run Python applications in isolated environments.
(If you're familiar with Node.js's `npx` tool, it's the same idea.)

This ensures that `valohai-cli`'s dependencies don't conflict with other Python packages.

Once you have installed and configured `pipx` (see the link above), you can

```bash
$ pipx install valohai-cli
```

and to upgrade it later on,

```bash
$ pipx upgrade valohai-cli
```

### System-wide or user-wide installation with pip

You can also install `valohai-cli` system-wide with `pip`,
but this may cause conflicts with other Python packages installed
system-wide or user-wide.

```bash
$ pip3 install -U valohai-cli
```

The `-U` flag ensures that any present version is upgraded, too.

### Installation in a virtual environment

If you prefer to install `valohai-cli` in a virtual environment, you can do so with `pip` as well.

```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -U valohai-cli
```

## Getting Started

After you've installed the client, `vh` should work and you should see a description
of commands.

See the [tutorial document](./TUTORIAL.md)!

[vh]: https://valohai.com/
[app]: https://app.valohai.com/

## Developing

Development requires Python 3.10+; otherwise you'll get false positive type failures.
CI will run tests on older Python versions.

To work on the `valohai-cli` code: pull the repository, create and activate a virtualenv, then run:

```bash
make dev
```

This installs `valohai-cli` as an "editable" `vh` command available in the virtualenv, but linked to
the working copy's source. That is, you can now edit the source under `valohai_cli` in your working
directory, and try it out with `vh`.

```bash
vh --help
# Usage: vh [OPTIONS] COMMAND [ARGS]...
```

To run lints, type checks and tests:

```bash
# run linting and type checks
make lint

# run tests
make test
```

[pipx]: https://github.com/pypa/pipx
