import codecs
import contextlib
import json
import os
from errno import ENOENT
from typing import Any, Callable, Optional


class Persistence:
    def __init__(self, data: Optional[dict] = None) -> None:
        self._data = data

    @property
    def data(self) -> dict:
        if self._data is None:
            self._data = {}
        return self._data

    def update(self, data: Optional[dict] = None, **kwargs: Any) -> None:
        self.data.update((data or {}), **kwargs)

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def save(self) -> None:
        pass


class FilePersistence(Persistence):
    def __init__(self, get_filename: Callable[[], str]) -> None:
        super().__init__()
        self.get_filename = get_filename

    @property
    def data(self) -> dict:
        if self._data is None:
            self._load()
        assert self._data is not None
        return self._data

    def _load(self) -> None:
        filename = self.get_filename()
        try:
            with codecs.open(filename, "r", encoding="UTF-8") as infp:
                self._data = json.load(infp)
        except OSError as ee:
            if ee.errno != ENOENT:
                raise
            self._data = {}
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"could not read configuration file {filename}") from exc

    def save(self) -> None:
        filename = self.get_filename()
        first_save = not os.path.isfile(filename)
        with codecs.open(filename, "w", encoding="UTF-8") as outfp:
            json.dump(self.data, outfp, ensure_ascii=False, indent=2, sort_keys=True)
        if first_save:
            with contextlib.suppress(Exception):
                os.chmod(filename, 0o600)
