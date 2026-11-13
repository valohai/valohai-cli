# Development

## Setting up

This project is written in Python 3.10+.

```bash
make dev
# installs the package in editable mode with test extras (`.[test]`) plus prek,
# using `uv pip` if uv is available and `pip` otherwise.
# Now you will have the `vh` command in your venv.

# for local development, you need to specify the login endpoint in `--host` / `-h`, i.e.
vh login --host http://localhost:8000
```

Without `make`, the equivalent is:

```bash
pip install -e .[test] prek
prek install
```

## Testing

PyTest is used for running tests. Test dependencies are in the `test` extra in `pyproject.toml`.

```bash
make test
# or just
pytest
```

## Linting

```bash
make lint
# runs `prek run --all-files`
```
