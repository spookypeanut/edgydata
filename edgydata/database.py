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
"""
CREATE TABLE purchased (
    time time,
        value float,
            site_id integer
            );

            CREATE TABLE consumption (
                    time time,
                    value float,
                    site_id integer
            );

            CREATE TABLE self_consumption (
                    time time,
                    value float,
                    site_id integer
            );

            CREATE TABLE production (
                    time time,
                    value float,
                    site_id integer
            );

            CREATE TABLE feed_in (
                    time time,
                    value float,
                    site_id binary
            );

            CREATE TABLE sites (
                    id integer,
                    name string,
                    peak_power float,
                    installation_date date,
                    last_update_time time,
                    lifetime_energy float
            );

"""
