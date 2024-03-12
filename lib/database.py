import sqlite3

import exceptions


class SqliteType:
    """Wrappter type for Sqlite column types"""

    def __init__(self, value: str):
        self._value = value.lower()

        # sqlite has `int` and `integer` type that are basiccaly the same
        if self._value == "int":
            self._value = "integer"

    def __eq__(self, __x: object) -> bool:
        if isinstance(__x, SqliteType) and __x._value == self._value:
            return True
        elif self._value == "text" and isinstance(__x, str):
            return True
        elif self._value == "integer" and isinstance(__x, int):
            return True
        elif self._value == "real" and (isinstance(__x, float) or isinstance(__x, int)):
            return True
        elif self._value == "datetime" and isinstance(__x, str):
            return True
        elif self._value == "blob" and isinstance(__x, bytes):
            return True
        elif self._value == "any":
            return True
        else:
            return False

    def __str__(self) -> str:
        return self._value


class Database:
    """Object to interact with the sqlite database"""

    def __init__(
        self, path: str = "database.db", max_pending=10_000, table=None
    ) -> None:
        self._db = sqlite3.connect(
            path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self._db.execute("PRAGMA journal_mode=wal")

        self._table = table

        self._pending = 0
        self._max_pending = max_pending

    def __del__(self):
        """Close the db on exit"""

        # check if there are uncommitted changes
        if self._db.in_transaction:
            self._db.commit()

        self._db.close()

    def _commit(self) -> None:
        """Write the file (commit) only if there are a proper amount of pending changes"""

        self._pending += 1

        if self._pending > self._max_pending:
            try:
                self._db.commit()
                self._pending = 0
            except sqlite3.DatabaseError:
                # if database is locked continue and try to
                # commit on the next change
                pass

    def _table_info(self, table=None) -> dict:
        """Retrive information from a table of the db. If there is no such table raise an exception

        :param table: name of the table to investigate
        """

        if table is None:
            table = self._table

        raw_info = self._db.execute(f"PRAGMA table_info({table})").fetchall()

        if len(raw_info) == 0:
            raise exceptions.DatabaseInfoError(table)

        col_names = [v[1] for v in raw_info]
        col_types = [SqliteType(v[2]) for v in raw_info]

        return {"names": col_names, "types": col_types}

    def _check_insert_data(self, table: str, data: list or tuple or dict) -> bool:
        """Check if the types from the data are compatible with the type of the table

        :param table: table to retrive info
        :param data: data to check types
        """

        names, types = self._table_info(table).values()

        # len data check
        if len(data) != len(names):
            return False

        if isinstance(data, dict) and names != list(data.keys()):
            return False

        # type data check, it uses `SqliteType` to make a fast compare
        if isinstance(data, dict):
            values = list(data.values())
            return all((t == values[i] for i, t in enumerate(types)))
        elif isinstance(data, list) or isinstance(data, tuple):
            return all((t == data[i] for i, t in enumerate(types)))

    def insert_data(self, data: list or tuple or dict = None) -> None:
        """Insert a new row into the db table (USE THIS!)

        **This is the hig level insert with table fields type checking**

        :param data: ordered iterable with the data to write
        """

        if self._table is None or data is None:
            raise exceptions.DatabaseError

        if not self._check_insert_data(self._table, data):
            raise exceptions.DatabaseDataError

        if isinstance(data, dict):
            data = tuple(data.values())

        self.insert(self._table, data)

    def insert(self, table: str = None, data: list or tuple = None) -> None:
        """Insert a new row into the db table

        **This is a low level insert without table fields type checking**

        :param table: name of the table to write
        :param data: ordered list with the data to write
        """

        if table is None or data is None:
            raise exceptions.DatabaseError

        # fill the query with the qmark
        values = ",".join(["?"] * len(data))

        try:
            self._db.execute(f"INSERT INTO {table} VALUES ({values})", data)
        except sqlite3.OperationalError as e:
            raise exceptions.DatabaseDataError(e)

        # evaluate commit if there are enough pending changes
        self._commit()

    def select(self, table: str = None, range_: tuple = None) -> list:
        """Read a range of rows of the table, if a range is not provided return the entire table.

        **Range need a table with and `id` field**

        :param table: name of the table to read
        :param range: inclusive range of value to read in the form `(start, end)`[default=None]
        """

        if table is None:
            table = self._table

        # normal select for all values

        if range_ is None:
            return self._db.execute(f"SELECT * FROM {table}").fetchall()

        # using range for values

        if not isinstance(range_, tuple) and len(range_) != 2:
            raise exceptions.DatabaseError

        start, end = range_

        return self._db.execute(
            f"SELECT * FROM {table} WHERE id >= {start} AND id <= {end}"
        ).fetchall()

    def config(self, module: str = None) -> dict:
        """Retrive the configuration of the bike, this always return the `global` configuration

        :param module: identify the configuration of the module"""

        # global config
        config = eval(
            self._db.execute(
                f'SELECT value FROM configuration WHERE module == "global"'
            ).fetchone()[0]
        )

        if module:
            module_conf = eval(
                self._db.execute(
                    f'SELECT value FROM configuration WHERE module == "{module}"'
                ).fetchone()[0]
            )

            config.update(module_conf)

        return config