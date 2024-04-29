class CoreError(Exception):
    pass


# DATABASE EXCEPTIONS

import sqlite3


class DatabaseError(CoreError, sqlite3.Error):
    pass


class DatabaseInfoError(DatabaseError):
    __DEFAULT_MESSAGE = "Unable to retrive information from table `{}`"

    def __init__(self, table: str = None, _message=__DEFAULT_MESSAGE):
        CoreError.__init__(self, _message.format(table))


class DatabaseDataError(DatabaseError):
    __DEFAULT_MESSAGE = "Unable to insert data into database"

    def __init__(self, _message=__DEFAULT_MESSAGE):
        CoreError.__init__(self, _message)