import sqlite3
import os


class DatabaseConnection:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            db_path = os.path.join(os.path.dirname(__file__), "..", "..", "pagos.db")
            cls._connection = sqlite3.connect(db_path, check_same_thread=False)
            cls._connection.row_factory = sqlite3.Row
        return cls._instance

    @property
    def connection(self):
        return self._connection

    def close(self):
        if self._connection:
            self._connection.close()
            DatabaseConnection._instance = None
            DatabaseConnection._connection = None
