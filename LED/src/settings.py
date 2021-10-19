from .common_files.common_settings import CommonSettings


class Settings(CommonSettings):
    @property
    def mode(self) -> int:
        return self._values['mode'] \
            if self._values.__contains__('mode') \
               and isinstance(self._values['mode'], int) \
            else 0
