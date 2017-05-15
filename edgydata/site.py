from copy import deepcopy
from edgydata.base import AbstractSolarEdge, BASE_URL, ResponseError
from edgydata.time import date_from_string, datetime_to_string
from datetime import timedelta


def _combine_power_details(first, second):
    # Check everything is as it should be
    should_have = set(["meters", "timeUnit", "unit"])
    if set(first.keys()) != should_have:
        raise ResponseError("API gave back weird results: %s" % first.keys())
    if set(second.keys()) != should_have:
        raise ResponseError("API gave back weird results: %s" % second.keys())
    if first["unit"] != second["unit"]:
        raise ResponseError("Units differ between power details")
    if first["timeUnit"] != second["timeUnit"]:
        raise ResponseError("Time units differ between power details")

    return_dict = deepcopy(first)
    return_dict["meters"] = []
    for meter in [a for a in first["meters"]]:
        type_ = meter["type"]
        toupdate = [a["values"] for a in first["meters"]
                    if a["type"] == type_][0]
        if len(toupdate[-1]) == 1:
            # For some reason, the last entry doesn't have a value. So
            # we need a (single point) overlap, and we clean out the
            # last point
            toupdate = toupdate[:-1]
        updatewith = [a["values"] for a in second["meters"]
                      if a["type"] == type_][0]
        toupdate.extend(updatewith)
        return_dict["meters"].append({"type": type_, "values": toupdate})
    return return_dict

class Site(AbstractSolarEdge):
    def __init__(self, api_key, site_id):
        AbstractSolarEdge.__init__(self, api_key)
        self._site_id = site_id

    def _get_url(self, function):
        kwargs = {"base": BASE_URL, "site_id": self._site_id,
                  "function": function}
        return "{base}/site/{site_id}/{function}.json".format(**kwargs)

    def _call(self, function, data=None):
        if data is None:
            response = self._raw_call(self._get_url(function), {})
        else:
            response = self._raw_call(self._get_url(function), data)
        return response[function]

    def get_details(self):
        return self._call("details")

    def get_data_period(self):
        results = self._call("dataPeriod")
        return_dict = {}
        for key, value in results.items():
            return_dict[key] = date_from_string(value)
        return (return_dict["startDate"], return_dict["endDate"])

    def get_power_details(self, start_time, end_time):
        if end_time <= start_time:
            raise ValueError("Please get your times the right way round")
        if (end_time - start_time).days >= 28:
            # The time span is large for the SolarEdge API, so split it
            # up over multiple calls and rejoin at the end
            middle = start_time + timedelta(days=27)
            details_one = self.get_power_details(start_time, middle)
            details_two = self.get_power_details(middle, end_time)
            return _combine_power_details(details_one, details_two)
        params = {"startTime": datetime_to_string(start_time),
                  "endTime": datetime_to_string(end_time)}
        results = self._call("powerDetails", params)
        return results

    def get_all_power_details(self):
        start, end = self.get_data_period()
        return self.get_power_details(start, end)
