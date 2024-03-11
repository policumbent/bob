import time as pytime

from datetime import datetime as dt, timezone as tz


class time:
    """General representation of time for congruence of data"""

    @classmethod
    def _unix_time(cls):
        """Return the unix time (https://en.wikipedia.org/wiki/Unix_time)"""
        return pytime.time()

    @classmethod
    def _human_time(cls, _curr=None):
        """Return the current utc time

        :param _curr: unix time to convert, mostly used for debug [default=None]
        """

        if _curr:
            return dt.fromtimestamp(_curr, tz.utc).time()
        else:
            return dt.utcnow().time()

    @classmethod
    def timestamp(cls, _curr=None):
        """Return the current unix time truncated to milliseconds `xxxxxxxxxx.sss`

        :param _curr: unix time to convert, mostly used for debug [default=None]
        """

        now = _curr if _curr else cls._unix_time()
        sec, mill = str(now).split(".")

        # truncate secs to millis
        mill = mill[:3]

        return f"{sec}.{mill}"

    @classmethod
    def human_timestamp(cls, _curr=None):
        """Return the current utc time in human readable format `HH:MM:SS.sss`

        :param _curr: unix time to convert, mostly used for debug [default=None]
        """

        now = cls._human_time(_curr)
        hh, mm, ss = str(now).split(":")

        # truncate secs to millis
        ss = ss[:6]

        return f"{hh}:{mm}:{ss}"