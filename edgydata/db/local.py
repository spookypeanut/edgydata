import os
import sqlite3
from datetime import date, datetime
from edgydata.constants import POWER_TYPES
from edgydata.data import Site
from edgydata.db.abstract import Abstract as AbstractDB

_TYPE_LOOKUP = {str: "STRING", int: "INTEGER", float: "FLOAT",
                date: "DATE"}


def _date_to_int(mydate):
    """ Convert a datetime.date object to a unix timestamp """
    return _datetime_to_int(datetime.combine(mydate, datetime.min.time()))


def _datetime_to_int(mytime):
    """ Convert a datetime.datetime object to a unix timestamp. """
    # Apparently, this is the safest way to do it (ignoring timezones)
    return int((mytime - datetime(1970, 1, 1)).total_seconds())


def _int_to_datetime(myint):
    """ Convert a unix timestamp to a datetime.datetime object """
    return datetime.fromtimestamp(myint)


def _int_to_date(myint):
    """ Convert a unix timestamp to a datetime.date object """
    return _int_to_datetime(myint).date()

# The converters to use to put object types into and get them out of the
# database. First element is to put them in, second to get them out
_CONVERTER = {date: (_date_to_int, _int_to_date),
              datetime: (_datetime_to_int, _int_to_datetime)}


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


class Local(AbstractDB):
    """ A local mirror of the solar power data, stored in a sqlite database.
    The intention is that the extraction API is the same as
    `edgydata.db.remote.Remote`, but there isn't any benefit to using
    inheritance here.
    """
    site_table = "site"
    power_table = "power"

    def __init__(self, path=None, debug=True):
        # If we get given a path, use it, but we can make up our own
        if path is None:
            self._dbpath = get_db_path()
        else:
            self._dbpath = path
        self._conn = sqlite3.connect(self._dbpath)
        self._cursor = self._conn.cursor()
        AbstractDB.__init__(self, debug=debug)

    def _execute(self, sql, variables=None):
        """ Execute an sql query, after optionally printing it """
        self.debug("Executing:")
        self.debug(sql)
        if variables is None:
            return_value = self._cursor.execute(sql)
        else:
            print("Variables:")
            print(variables)
            return_value = self._cursor.execute(sql, variables)
        self._conn.commit()
        return return_value

    def is_present(self):
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
            print("No database present at %s" % self._dbpath)

    def _create_site_table(self):
        table_name = _check(self.site_table)

        columns = []
        # We need to make sure we get the order correct
        for myattr in Site.list_attrs():
            mytype = Site.attr_types()[myattr]
            columns.append("%s %s" % (myattr, _TYPE_LOOKUP[mytype]))
        sql = ["CREATE TABLE %s (" % table_name,
               ",\n".join(columns),
               ", PRIMARY KEY (site_id))"]
        return self._execute("\n".join(sql))

    def _create_power_table(self):
        columns = []
        for col in POWER_TYPES:
            columns.append("%s FLOAT" % _check(col))

        sql = """ CREATE TABLE %s (
                    id INT NOT NULL PRIMARY KEY,
                    time TIME,
                    duration INT,
                    %s,
                    site_id INTEGER
            );""" % (_check(self.power_table), ",\n".join(columns))
        return self._execute(sql)

    def create(self):
        assert not self.is_present()

        self._create_site_table()
        self._create_power_table()

    def update(self):
        pass

    def _add_site_to_db(self, site):
        results = []
        for key in site.list_attrs():
            value = getattr(site, key)
            if value.__class__ in _CONVERTER:
                results.append(_CONVERTER[value.__class__][0](value))
            else:
                results.append(value)
        sql = "INSERT INTO %s VALUES (?, ?, ?, ?, ?)"
        sql = sql % _check(self.site_table)
        self._execute(sql, results)
        self._conn.commit()

    def _store_results_in_db(self, site_id, results):
        """ Store output from get_all_power_details into the local database """
