import os
import sqlite3


def get_db_path():
    return os.path.join(os.environ["HOME"], "edgydata.db")


class LocalDatabase(object):
    site_table = "sites"
    data_tables = set(["consumption", "self_consumption", "production",
                       "feed_in"])

    def __init__(self, path=None):
        if path is None:
            self._dbpath = get_db_path()
        else:
            self._dbpath = path
        self._conn = sqlite3.connect(self._dbpath)
        self._cursor = self._conn.cursor()

    def is_present(self):
        pass

    def _create_site_table(self):
        sql = """ CREATE TABLE %ss (
                    id integer,
                    name string,
                    peak_power float,
                    installation_date date,
                    last_update_time time,
                    lifetime_energy float
            );""" % self.site_table
        self._cursor.execute(sql)

    def _create_data_table(self, name):
        sql = """ CREATE TABLE %s (
                    time time,
                    value float,
                    site_id integer
            );""" % name
        self._cursor.execute(sql)

    def create(self):
        assert not self.is_present()

        self._create_site_table()
        for name in self.data_tables:
            self._create_data_table(name)
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
