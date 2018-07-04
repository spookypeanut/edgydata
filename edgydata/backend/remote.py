import os
import requests
from datetime import datetime, timedelta
from copy import deepcopy

from edgydata.data import Site, PowerPeriod
from edgydata.constants import POWER
from edgydata.backend.abstract import Abstract as AbstractBE
from edgydata.lib import date_to_datetime

BASE_URL = "https://monitoringapi.solaredge.com"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
# SolarEdge returns its values in a strange way. These next globals help us
# decode those
# Number of minutes in the listed time units
TIMEUNITS = {"QUARTER_OF_AN_HOUR": 0.25}
POWERUNITS = {"W": 1, "kW": 1000}
LOOKUP = {"Consumption": POWER.consumed, "FeedIn": POWER.exported,
          "Production": POWER.generated, "Purchased": POWER.imported,
          "SelfConsumption": POWER.self_consumed}


def _date_to_string(input_date):
    return input_date.strftime(DATE_FORMAT)


def _date_from_string(input_string):
    return datetime.strptime(input_string, DATE_FORMAT).date()


def _datetime_to_string(input_datetime):
    return input_datetime.strftime(DATETIME_FORMAT)


def _datetime_from_string(input_string):
    return datetime.strptime(input_string, DATETIME_FORMAT)


class ResponseError(IOError):
    """ The response from SolarEdge was not in the form we expected """


class Remote(AbstractBE):
    def __init__(self, api_key=None, debug=False):
        AbstractBE.__init__(self, debug=debug)
        if api_key is None:
            try:
                self._api_key = os.environ["SOLAREDGEAPI"]
            except KeyError:
                raise IOError("Cannot find a SolarEdge API key")
        else:
            self._api_key = api_key

    def _remote_call(self, sub_url, data=None):
        if data is None:
            data = {}
        url = "%s/%s" % (BASE_URL, sub_url)
        data_with_api = deepcopy(data)
        data_with_api.update({"api_key": self._api_key})
        response = requests.get(url, params=data_with_api)
        if not response.ok:
            self.warning(response.content)
            raise ResponseError("API call failed: %s" % response.reason)
        return response.json()

    def _get_site_id(self):
        """ A convenience method to select the only site id if there is only
        one. If there are more than one, raises an exception.
        """
        ids = self.get_site_ids()
        if len(ids) == 1:
            return ids[0]
        msg = "More than one site found: please use get_sites() and choose"
        raise ValueError(msg)

    def get_site_ids(self):
        """ Get all the site ids of all the sites connected with this SolarEdge
        account
        """
        data = self._remote_call("sites/list")
        ids = [a["id"] for a in data["sites"]["site"]]
        # Return this as a list, in the same order as the API gives them
        return ids

    def get_site(self, site_id=None):
        """ Return a Site object from a given site id, by querying the details
        from the SolarEdge API
        """
        if site_id is None:
            site_id = self._get_site_id()
        sub_url = "site/%s/details.json" % site_id
        result = self._remote_call(sub_url)
        raw = result["details"]
        raw_start = raw["installationDate"]
        raw_end = raw["lastUpdateTime"]
        kwargs = {"site_id": site_id,
                  "name": raw["name"],
                  "start_date": _date_from_string(raw_start),
                  "end_date": _date_from_string(raw_end),
                  "peak_power": raw["peakPower"]}
        return Site(**kwargs)

    def get_time_limits(self, site_id=None):
        site = self.get_site(site_id=site_id)
        return (site.start_date, site.end_date)

    def get_power(self, site_id=None, start=None, end=None):
        # This is just a wrapper around the private _get_usage that
        # sanitizes the parameters
        if site_id is None:
            site_id = self._get_site_id()
        site = self.get_site(site_id)
        if start is None:
            start = date_to_datetime(site.start_date)
        if end is None:
            # Don't get an extra day: it will just give you empty data
            end = date_to_datetime(site.end_date)
        return self._get_usage(site_id, start, end)

    def _get_usage(self, site_id, start, end):
        now = datetime.now()
        if end > now:
            end = now
        return_data = []
        if (end - start).days > 28:
            middle = end - timedelta(days=27)
            return_data = self._get_usage(site_id, start, middle)
        else:
            middle = start
        data = {"startTime": _datetime_to_string(middle),
                "endTime": _datetime_to_string(end)}
        sub_url = "site/%s/powerDetails.json" % site_id
        raw = self._remote_call(sub_url, data)["powerDetails"]
        meters = [m["type"] for m in raw["meters"]]
        # This next sorry section is just to get a list of all times in
        # the data. I could probably just get them from one of the
        # meters, but I've always been one for obsessive over-caution.
        alldump = []
        for dump in [m["values"] for m in raw["meters"]]:
            alldump.extend(dump)
        dates = set([d["date"] for d in alldump])

        duration = TIMEUNITS[raw["timeUnit"]]
        units = POWERUNITS[raw["unit"]]

        datedata = {}
        for eachdate in dates:
            datedata[eachdate] = {}
            for eachm in meters:
                meterdata = [r for r in raw["meters"] if r["type"] == eachm][0]
                datum = [m for m in meterdata["values"] if
                         m["date"] == eachdate][0]
                if "value" in datum:
                    # Convert value into Watts, in case it's not already
                    datum = datum["value"] * units
                else:
                    # For some reason, SolarEdge don't give a value when
                    # it's zero
                    datum = 0
                datedata[eachdate][eachm] = datum
        for date, data in datedata.items():
            kwargs = {"site_id": site_id}
            kwargs["start_time"] = _datetime_from_string(date)
            kwargs["duration"] = timedelta(hours=duration)
            for start, end in LOOKUP.items():
                try:
                    kwargs[end.name] = data[start]
                except Exception:
                    self.debug(date)
                    self.debug(data)
                    self.debug(start)
                    self.debug(end)
                    raise
            try:
                return_data.append(PowerPeriod(**kwargs))
            except Exception:
                self.debug(kwargs)
                raise
        return return_data
