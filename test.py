from datetime import datetime
import os
from edgydata import account
from edgydata.site import _combine_power_details
from pprint import pprint

sea = account.Account(os.environ["SOLAREDGEAPI"])
mysite = sea.get_sites()[0]
start = datetime(2017, 5, 12, 10, 0, 0)
end = datetime(2017, 5, 12, 11, 0, 0)
pd1 = mysite.get_power_details(start_time=start, end_time=end)
start = datetime(2017, 5, 12, 11, 0, 0)
end = datetime(2017, 5, 12, 12, 0, 0)
pd2 = mysite.get_power_details(start_time=start, end_time=end)
pd = _combine_power_details(pd1, pd2)
pprint(pd)
