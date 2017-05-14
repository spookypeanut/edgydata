import requests
from copy import deepcopy

BASE_URL = "https://monitoringapi.solaredge.com"


class ResponseError(IOError):
    """ The response from SolarEdge was not in the form we expected """

class AbstractSolarEdge(object):
    def __init__(self, api_key):
        self._api_key = api_key

    def _raw_call(self, url, data):
        data_with_api = deepcopy(data)
        data_with_api.update({"api_key": self._api_key})
        response = requests.get(url, params=data_with_api)
        if not response.ok:
            print(response.content)
            raise ResponseError("API call failed: %s" % response.reason)
        return response.json()
