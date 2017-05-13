from edgydata.base import AbstractSolarEdge, BASE_URL


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

