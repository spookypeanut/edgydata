from edgydata import AbstractSolarEdge

BASEURL = "https://monitoringapi.solaredge.com/site/{site_id}/{function}.json"


class EdgySite(AbstractSolarEdge):
    def __init__(self, api_key, site_id):
        AbstractSolarEdge.__init__(self, api_key)
        self._site_id = site_id

    def _get_url(self, function):
        kwargs = {"site_id": self._site_id, "function": function}
        return BASEURL.format(**kwargs)

    def get_details(self):
        return self._call("details")

    def _call(self, function, data=None):
        if data is None:
            response = self._raw_call(self._get_url(function), {})
        else:
            response = self._raw_call(self._get_url(function), data)
        return response[function]
