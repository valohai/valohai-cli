# Development

## Setting up
This project is written in Python 3.5 and contains tests runs in Python 3.5, 3.6 and 3.7. Create a virtualenv using Python 3.5 to get started.

```bash
pip install -e .
# now you will have executable `vh` command in your venv

# for local development, you need to specify the login endpoint in `--host` / `-h`, i.e.
vh login --host http://localhost:8000
```

## Testing
PyTest and Tox are used for running tests with the above mentioned Python versions. They are included in `requirements-dev.txt`.

```bash
pip install -r requirements-dev.txt
pytest
tox
```
