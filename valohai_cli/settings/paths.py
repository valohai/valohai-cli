import os
import sys


def get_settings_root_path() -> str:  # pragma: no cover
    if sys.platform == "win32":
        return os.path.normpath(os.environ["LOCALAPPDATA"])
    elif sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/")
    else:
        return os.getenv("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))


def get_settings_file_name(name: str) -> str:
    path = os.environ.get("VALOHAI_CONFIG_DIR")
    if path:
        if not os.path.isdir(path):
            raise ValueError(f"Directory {path} does not exist")
    else:
        path = os.path.join(get_settings_root_path(), "valohai-cli")
        if not os.path.isdir(path):
            os.makedirs(path, 0o700)
    return os.path.join(path, name)
