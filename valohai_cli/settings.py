import json
import os

import sys


def get_settings_file_name(name='.valohai-cli.json'):  # pragma: no cover
    path = os.environ.get('VALOHAI_CONFIG_DIR')
    if path:
        if not os.path.isdir(path):
            raise ValueError('Directory %s does not exist' % path)
    elif sys.platform == 'win32':
        path = os.path.normpath(os.environ['LOCALAPPDATA'])
    elif sys.platform == 'darwin':
        path = os.path.expanduser('~/Library/Application Support/')
    else:
        path = os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
        os.makedirs(path, 0o700, exist_ok=True)
    return os.path.join(path, name)


class BaseSettings:
    def __init__(self):
        self._data = None

    def get_filename(self):  # pragma: no cover
        raise NotImplementedError('...')

    @property
    def data(self):
        if self._data is None:
            self._load()
        return self._data

    def _load(self):
        filename = self.get_filename()
        try:
            with open(filename, 'r', encoding='UTF-8') as infp:
                self._data = json.load(infp)
        except FileNotFoundError:
            self._data = {}
        except Exception as exc:  # pragma: no cover
            raise RuntimeError('could not read configuration file %s' % filename) from exc

    def save(self):
        filename = self.get_filename()
        with open(filename, 'w', encoding='UTF-8') as outfp:
            json.dump(self.data, outfp, ensure_ascii=False, indent=2, sort_keys=True)


class Settings(BaseSettings):
    def get_filename(self):  # pragma: no cover
        return get_settings_file_name()

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def update(self, data=None, **kwargs):
        self.data.update((data or {}), **kwargs)


settings = Settings()
