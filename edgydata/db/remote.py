import os
import requests
from copy import deepcopy

from edgydata.data import Site

BASE_URL = "https://monitoringapi.solaredge.com"


class ResponseError(IOError):
    """ The response from SolarEdge was not in the form we expected """


class Remote(object):
    def __init__(self, api_key=None):
        if api_key is None:
            try:
                self._api_key = os.environ["SOLAREDGEAPI"]
            except KeyError:
                raise IOError("Cannot find a SolarEdge API key")
        else:
            self._api_key = api_key

    def _remote_call(self, sub_url, data):
        url = "%s/%s" % (BASE_URL, sub_url)
        data_with_api = deepcopy(data)
        data_with_api.update({"api_key": self._api_key})
        response = requests.get(url, params=data_with_api)
        if not response.ok:
            print(response.content)
            raise ResponseError("API call failed: %s" % response.reason)
        return response.json()

    def _get_site_ids(self):
        """ Get all the site ids of all the sites connected with this SolarEdge
        account
        """
        data = self._remote_call("sites/list", {})
        ids = [a["id"] for a in data["sites"]["site"]]
        # Return this as a list, in the same order as the API gives them
        return ids

    def get_sites(self):
        """ Return Site objects for all the sites connected with this SolarEdge
        account
        """
        for site_id in self._get_site_ids():
            yield self.get_site(site_id)

    def get_site(self, site_id):
        """ Return a Site object from a given site id, by querying the details
        from the SolarEdge API
        """
        pass
