# Valohai Command Line Client

More info at https://valohai.com/

## Development

```bash
pip install -e .
# now you will have executable `vh` command in your venv

# for local development, you need to specify the login endpoint in `--host` / `-h`
vh login --host http://localhost:8000
```

## Testing

```bash
pip install -r requirements-dev.txt
pytest
tox
```
