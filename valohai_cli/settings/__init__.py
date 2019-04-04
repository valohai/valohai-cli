from .paths import get_settings_file_name
from .persistence import FilePersistence


class Settings:
    def __init__(self, persistence=None):
        """

        :param persistence:
        """
        if not persistence:
            persistence = FilePersistence(get_filename=lambda: get_settings_file_name('config.json'))

        self.persistence = persistence

    @property
    def user(self):
        """
        The logged in user (dictionary or None).
        :rtype: dict|None
        """
        return self.persistence.get('user')

    @property
    def host(self):
        """
        The host we're logged in to (string or None if not logged in).
        :return:
        """
        return self.persistence.get('host')

    @property
    def token(self):
        """
        The authentication token we have for the host we're logged in to.
        """
        return self.persistence.get('token')

    @property
    def links(self):
        """
        Dictionary of directory <-> project object dicts.
        """
        return self.persistence.get('links', {})


settings = Settings()
