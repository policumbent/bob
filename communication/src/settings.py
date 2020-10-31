from .common_settings import CommonSettings


class Settings(CommonSettings):
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
    def server_port(self) -> int:
        return self._values['server_port'] \
            if self._values.__contains__('server_port') \
               and isinstance(self._values['server_port'], int) \
            else 443