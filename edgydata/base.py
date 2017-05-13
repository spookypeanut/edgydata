import requests
from copy import deepcopy
from datetime import datetime

BASE_URL = "https://monitoringapi.solaredge.com"

def date_from_string(input_string):
    return datetime.strptime(input_string, "%Y-%m-%d").date()

def datetime_from_string(input_string):
    raise NotImplementedError

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
