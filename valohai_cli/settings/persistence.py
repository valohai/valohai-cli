import codecs
import json
import os
from errno import ENOENT


class Persistence:
    def __init__(self, data=None):
        self._data = data

    @property
    def data(self):
        if self._data is None:
            self._data = {}
        return self._data

    def update(self, data=None, **kwargs):
        self.data.update((data or {}), **kwargs)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

    def save(self):
        pass


class FilePersistence(Persistence):
    def __init__(self, get_filename):
        super().__init__()
        self.get_filename = get_filename

    @property
    def data(self):
        if self._data is None:
            self._load()
        return self._data

    def _load(self):
        filename = self.get_filename()
        try:
            with codecs.open(filename, 'r', encoding='UTF-8') as infp:
                self._data = json.load(infp)
        except OSError as ee:
            if ee.errno != ENOENT:
                raise
            self._data = {}
        except Exception as exc:  # pragma: no cover
            raise RuntimeError('could not read configuration file %s' % filename) from exc

    def save(self):
        filename = self.get_filename()
        first_save = not os.path.isfile(filename)
        with codecs.open(filename, 'w', encoding='UTF-8') as outfp:
            json.dump(self.data, outfp, ensure_ascii=False, indent=2, sort_keys=True)
        if first_save:
            try:
                os.chmod(filename, 0o600)
            except Exception:
                pass
