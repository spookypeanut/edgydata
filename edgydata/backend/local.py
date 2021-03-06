import os
import sys

import sqlite3
from datetime import date, datetime, timedelta

from edgydata.backend.abstract import Abstract as AbstractBE
from edgydata.constants import POWER_TYPES
from edgydata.data import Site, PowerPeriod
from edgydata.lib import batch
from edgydata.time import (date_to_int, int_to_date,
                           datetime_to_int, int_to_datetime,
                           timedelta_to_int, int_to_timedelta)

_TYPE_LOOKUP = {str: "STRING", int: "INTEGER", float: "FLOAT",
                date: "INTEGER", timedelta: "INTEGER"}

INSERTBATCHSIZE = 100

# The converters to use to put object types into and get them out of the
# database. First element is to put them in, second to get them out
_CONVERTER = {date: (date_to_int, int_to_date),
              datetime: (datetime_to_int, int_to_datetime),
              timedelta: (timedelta_to_int, int_to_timedelta)}


def _check(mystr):
    """ Ensure a string isn't trying to inject any dodgy SQL """
    # Although the input strings are all self-generated atm, this could
    # change in future
    if mystr != mystr.translate(None, ")(][;,"):
        raise RuntimeError("Input '%s' looks dodgy to me" % mystr)
    return mystr


def get_db_path():
    """ Get the file path to the sqlite database """
    return os.path.join(os.environ["HOME"], "edgydata.db")


class Local(AbstractBE):
    """ A local mirror of the solar power data, stored in a sqlite database.
    The intention is that the extraction API is the same as
    `edgydata.db.remote.Remote`, but there isn't any benefit to using
    inheritance here.
    """
    site_table = "site"
    power_table = "power"

    def __init__(self, path=None, debug=False):
        AbstractBE.__init__(self, debug=debug)
        # If we get given a path, use it, but we can make up our own
        if path is None:
            self._dbpath = get_db_path()
        else:
            self._dbpath = path
        self._connect_db()

    def _connect_db(self):
        self._conn = sqlite3.connect(self._dbpath)
        self._cursor = self._conn.cursor()

    def _execute(self, sql, variables=None, many=False):
        """ Execute an sql query, after optionally printing it """
        self.debug("Executing:")
        self.debug(sql)
        if variables is None:
            if many is True:
                return_value = self._cursor.executemany(sql)
            else:
                return_value = self._cursor.execute(sql)
        else:
            # TODO: Check if it's a tuple / iterable
            if not isinstance(variables, list):
                variables = [variables]
            self.debug("Variables: %s" % (variables,))
            if many is True:
                return_value = self._cursor.executemany(sql, variables)
            else:
                return_value = self._cursor.execute(sql, variables)
        self._conn.commit()
        return return_value

    def is_present(self):
        """ Check to see if the local database exists """
        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        self._execute(sql)
        if self._cursor.fetchall() == []:
            return False
        return True

    def destroy(self):
        if self.is_present():
            self._conn.close()
            os.remove(self._dbpath)
        else:
            self.warning("No database present at %s" % self._dbpath)

    def _create_site_table(self):
        table_name = _check(self.site_table)

        columns = []
        # We need to make sure we get the order correct
        for myattr in self._get_site_columns():
            mytype = Site.attr_types()[myattr]
            columns.append("%s %s" % (myattr, _TYPE_LOOKUP[mytype]))
        sql = ["CREATE TABLE %s (" % table_name,
               ",\n".join(columns),
               ", PRIMARY KEY (site_id))"]
        return self._execute("\n".join(sql))

    def _create_power_table(self):
        columns = []
        for col in sorted(POWER_TYPES):
            columns.append("%s FLOAT" % _check(col))

        sql = """ CREATE TABLE %s (
                    site_id INTEGER,
                    start_time INTEGER,
                    duration INTEGER,
                    %s,
                    PRIMARY KEY (site_id, start_time),
                    FOREIGN KEY (site_id) REFERENCES %s (site_id)
            );""" % (_check(self.power_table), ",\n".join(columns),
                     _check(self.site_table))
        return self._execute(sql)

    def create(self):
        """ Create the local database """
        try:
            assert not self.is_present()
            self._create_site_table()
            self._create_power_table()
        except sqlite3.ProgrammingError:
            # If we've just destroyed, we need to re-connect before
            # recreating
            self._connect_db()
            self.create()

    def add_site(self, site):
        results = []
        for key in self._get_site_columns():
            value = getattr(site, key)
            if value.__class__ in _CONVERTER:
                results.append(_CONVERTER[value.__class__][0](value))
            else:
                results.append(value)
        sql = "INSERT INTO %s VALUES (?, ?, ?, ?, ?)"
        sql = sql % _check(self.site_table)
        return self._execute(sql, results)

    def get_site(self, site_id=None):
        sql = "SELECT * FROM %s WHERE site_id = ?"
        sql = sql % _check(self.site_table)
        self._execute(sql, site_id)
        raw_tuples = self._cursor.fetchall()
        if len(raw_tuples) == 0:
            raise ValueError("Site %s not found in local database" % site_id)
        if len(raw_tuples) != 1:
            # This should never happen, since site_id is the primary key
            raise ValueError("Some seriously weird shit happened")
        raw_tuple = list(raw_tuples)[0]
        columns = self._get_site_columns()
        tmp_dict = dict(zip(columns, raw_tuple))
        tmp_dict["start_date"] = int_to_date(tmp_dict["start_date"])
        tmp_dict["end_date"] = int_to_date(tmp_dict["end_date"])
        print("tmp_dict")
        print(tmp_dict)
        return Site(**tmp_dict)

    def get_site_ids(self):
        sql = "SELECT DISTINCT(site_id) FROM %s"
        sql = sql % _check(self.site_table)
        self._execute(sql)
        raw_tuples = self._cursor.fetchall()
        return set([i[0] for i in raw_tuples])

    @classmethod
    def _get_site_columns(cls):
        return Site.list_attrs()

    @classmethod
    def _get_power_columns(cls):
        results = ["site_id", "start_time", "duration"]
        results.extend(sorted(POWER_TYPES))
        return results

    def _has_power(self, power):
        if self.get_power(site_id=power.site_id, start=power.start_time,
                          end=power.start_time):
            return True
        return False

    def add_power(self, power):
        """ Add an interable of power periods to the local database. Skip them
        if they're already in there.
        """
        msg = "Adding %s power periods to the local database" % len(power)
        self.info(msg)
        sorted_power = sorted(power)
        start = sorted_power[0].start_time
        end = sorted_power[-1].start_time + sorted_power[-1].duration
        msg = "From %s to %s" % (start, end)
        self.info(msg)
        for powerbatch in batch(power, INSERTBATCHSIZE):
            rows = []
            for eachpower in powerbatch:
                if self._has_power(eachpower):
                    self.warning("%s skipped as already present" % eachpower)
                    continue
                power_row = [eachpower.site_id,
                             datetime_to_int(eachpower.start_time),
                             timedelta_to_int(eachpower.duration)]
                for col in sorted(POWER_TYPES):
                    value = getattr(eachpower, col)
                    power_row.append(value)
                rows.append(power_row)
            sql = "INSERT INTO %s VALUES (?, ?, ?, %s)"
            more_args = ", ".join(["?"] * len(POWER_TYPES))
            sql = sql % (_check(self.power_table), more_args)
            print(sql)
            self._execute(sql, rows, many=True)

    def get_power(self, site_id=None, start=None, end=None):
        if start is None:
            start = 0
        else:
            start = datetime_to_int(start)
        if end is None:
            end = sys.maxint
        else:
            end = datetime_to_int(end)
        sql = "SELECT * FROM %s WHERE start_time >= %s AND start_time <= %s"
        sql = sql % (_check(self.power_table), start, end)
        self._execute(sql)
        raw_tuples = self._cursor.fetchall()
        return_set = set()
        columns = self._get_power_columns()
        for each_tuple in raw_tuples:
            tmp_dict = dict(zip(columns, each_tuple))
            tmp_dict["start_time"] = int_to_datetime(tmp_dict["start_time"])
            tmp_dict["duration"] = int_to_timedelta(tmp_dict["duration"])
            return_set.add(PowerPeriod(**tmp_dict))
        return return_set

    def _get_min_time(self, site_id=None):
        sql = "SELECT MIN(start_time) FROM %s" % _check(self.power_table)
        if site_id is not None:
            sql += " WHERE site_id == ?"
        self._execute(sql, site_id)
        as_int = self._cursor.fetchone()[0]
        if as_int is None:
            return None
        return int_to_datetime(as_int)

    def _get_max_time(self, site_id=None):
        sql = "SELECT MAX(start_time), duration FROM %s"
        if site_id is not None:
            sql += " WHERE site_id == ?"
        sql = sql % _check(self.power_table)
        # Luckily, if site_id is None, variables gets passed as None
        self._execute(sql, site_id)
        start_time, duration = self._cursor.fetchone()
        if start_time is None:
            return None
        return int_to_datetime(start_time + duration)

    def get_time_limits(self, site_id=None):
        return (self._get_min_time(site_id=site_id),
                self._get_max_time(site_id=site_id))
