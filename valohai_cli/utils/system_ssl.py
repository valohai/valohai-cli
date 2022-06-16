from requests.adapters import HTTPAdapter


class DefaultCertsHTTPAdapter(HTTPAdapter):
    # H/T: https://github.com/psf/requests/issues/2966#issuecomment-852624480

    def init_poolmanager(self, *args, **kwargs):
        import ssl

        ssl_context = ssl.create_default_context()
        ssl_context.load_default_certs()
        kwargs['ssl_context'] = ssl_context
        return super().init_poolmanager(*args, **kwargs)
