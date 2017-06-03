import os
import sqlite3


def get_db_path():
    return os.path.join(os.environ["HOME"], "edgydata.db")


class LocalDatabase(object):
    def __init__(self, path=None):
        if path is None:
            path = get_db_path()
        self._conn = sqlite3.connect(path)
        self._cursor = self._conn.cursor()
