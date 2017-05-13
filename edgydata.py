import requests
from copy import deepcopy
BASEURL = "https://monitoringapi.solaredge.com/site/{site_id}/{call}.json"


class AbstractSolarEdge(object):
    def __init__(self, api_key):
        self._api_key = api_key

    def _raw_call(self, url, data):
        data_with_api = deepcopy(data)
        data_with_api.update({"api_key": self._api_key})
        response = requests.get(url, params=data_with_api)
        if not response.ok:
            print(response.content)
            raise RuntimeError("API call failed: %s" % response.reason)
        return response.json()


class EdgyData(AbstractSolarEdge):
    def get_site_ids(self):
        url = "https://monitoringapi.solaredge.com/sites/list"
        data = self._raw_call(url, {})
        ids = [a["id"] for a in data["sites"]["site"]]
        # Return this as a list, in the same order as the API gives them
        return ids
