default:
	echo "Try another target"

mypy:
	mypy valohai_cli --exclude '.*vendor.*' --show-error-code --incremental --strict --disable-error-code=type-arg

lint:
	flake8