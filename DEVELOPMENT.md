# Development

## Setting up
This project is written in Python 3.6+.

```bash
pip install -e .
# now you will have executable `vh` command in your venv

# for local development, you need to specify the login endpoint in `--host` / `-h`, i.e.
vh login --host http://localhost:8000
```

## Testing
PyTest is used for running tests with the above mentioned Python versions. Development deps are in `requirements-dev.txt`.

```bash
pip install -r requirements-dev.txt
pytest
```
