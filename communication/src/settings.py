from .common_settings import CommonSettings


class Settings(CommonSettings):

    def __init__(self, values):
        self.bike = 'taurusx'
        super().__init__(values)

    @property
    def bike(self):
        return self.bike

    @bike.setter
    def bike(self, value):
        self._bike = value

    @property
    def cert(self) -> str:
        return self._values['cert'] \
            if self._values.__contains__('cert') \
               and isinstance(self._values['cert'], str) \
            else './cert.crt'

    @property
    def server_ip(self) -> str:
        return self._values['server_ip'] \
            if self._values.__contains__('server_ip') \
               and isinstance(self._values['server_ip'], str) \
            else '127.0.0.1'

    @property
    def protocol(self) -> str:
        return self._values['protocol'] \
            if self._values.__contains__('protocol') \
               and isinstance(self._values['protocol'], str) \
            else 'https'
    @property
    def username(self) -> str:
        return self._values['username'] \
            if self._values.__contains__('username') \
               and isinstance(self._values['username'], str) \
            else 'user'

    @property
    def password(self) -> str:
        return self._values['password'] \
            if self._values.__contains__('password') \
               and isinstance(self._values['password'], str) \
            else 'test'

    @property
    def base_path(self) -> str:
        return '{}://{}:{}/'.format(self.protocol, self.server_ip, self.server_port)

    @property
    def server_port(self) -> int:
        return self._values['server_port'] \
            if self._values.__contains__('server_port') \
               and isinstance(self._values['server_port'], int) \
            else 443

