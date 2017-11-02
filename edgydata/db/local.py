import os
import sqlite3
from edgydata.constants import POWER, POWER_TYPES


def _check(mystr):
    if mystr != mystr.translate(None, ")(][;,"):
        raise RuntimeError("Input '%s' looks dodgy to me" % mystr)
    return mystr


def get_db_path():
    return os.path.join(os.environ["HOME"], "edgydata.db")


class Local(object):
    site_table = "site"
    power_table = "power"

    def __init__(self, path=None):
        if path is None:
            self._dbpath = get_db_path()
        else:
            self._dbpath = path
        self._conn = sqlite3.connect(self._dbpath)
        self._cursor = self._conn.cursor()

    def _query(self, sql, variables=None):
        if variables is None:
            return_value = self._cursor.execute(sql)
        else:
            return_value = self._cursor.execute(sql, variables)
        self._conn.commit()
        return return_value

    def is_present(self):
        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        self._cursor.execute(sql)
        if self._cursor.fetchall() == []:
            return False
        return True

    def destroy(self):
        if self.is_present():
            self._conn.close()
            os.remove(self._dbpath)
        else:
            print("No database present at %s" % self._dbpath)

    def _create_site_table(self):
        sql = """ CREATE TABLE %s (
                    id integer,
                    name string,
                    peak_power float,
                    start_date date,
                    end_date date
            );""" % _check(self.site_table)
        return self._cursor.execute(sql)

    def _create_power_table(self):
        columns = []
        for col in POWER_TYPES:
            columns.append("%s float," % _check(col))

        sql = """ CREATE TABLE %s (
                    time time,
                    duration int,
                    %s
                    site_id integer
            );""" % (_check(self.power_table), "\n".join(columns))
        return self._cursor.execute(sql)

    def create(self):
        assert not self.is_present()

        self._create_site_table()
        self._create_power_table()

    def update(self):
        pass

    def _add_site_to_db(self, site):
        deets = site.get_details()
        # NB lifetime_energy doesn't come from the same place, so using
        # peakPower as placeholder
        attrs = ["id", "name", "peakPower", "installationDate",
                 "lastUpdateTime", "peakPower"]
        results = []
        for key in attrs:
            results.append(deets[key])
        sql = "INSERT INTO %s VALUES (?, ?, ?, ?, ?, ?)"
        sql = sql % _check(self.site_table)
        self._cursor.execute(sql, results)
        self._conn.commit()

    def _store_results_in_db(self, site_id, results):
        """ Store output from get_all_power_details into the local database """
