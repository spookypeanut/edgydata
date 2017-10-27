import os
import requests
from copy import deepcopy
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

BASE_URL = "https://monitoringapi.solaredge.com"


class ResponseError(IOError):
    """ The response from SolarEdge was not in the form we expected """

def remote_call(self, url, data, api_key=None):
    if api_key is None:
        try:
            api_key = os.environ["SOLAREDGEAPI"]
        except KeyError:
            raise IOError("Cannot find a SolarEdge API key")
    data_with_api = deepcopy(data)
    data_with_api.update({"api_key": api_key})
    response = requests.get(url, params=data_with_api)
    if not response.ok:
        print(response.content)
        raise ResponseError("API call failed: %s" % response.reason)
    return response.json()


def date_from_string(input_string):
    return datetime.strptime(input_string, DATE_FORMAT).date()


def datetime_from_string(input_string):
    raise NotImplementedError


def date_to_string(input_date):
    return input_date.strftime(DATE_FORMAT)


def datetime_to_string(input_datetime):
    return input_datetime.strftime(DATETIME_FORMAT)
