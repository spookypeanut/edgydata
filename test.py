""" A script created to test the edgydata database, but in doing so also
provide some interesting data
"""

from __future__ import print_function

from datetime import datetime, timedelta
from edgydata.backend.hybrid import Hybrid
from edgydata.visualize import chart
from edgydata.aggregate import aggregate
from edgydata.time import get_current_datetime


def main():
    """ Generate some interesting information about the data """
    myvalues = values()
    graphs()
    print(myvalues)


def values():
    """ Function that generates some interesting values from the data """
    # Examples of values to get:
    # Lowest generation in a day
    # Highest generation in a day
    # Day of the year that gives the lowest average generation
    # Day of the year that gives the highest average generation
    value_dict = {}
    hdb = Hybrid(debug=False)
    all_raw_data = hdb.get_power()
    from edgydata.aggregate import _has_duplicate_times
    if _has_duplicate_times(all_raw_data):
        raise ValueError
    highest_period = sorted(all_raw_data, key=lambda x: x.generated)[-1]
    high_period = highest_period.energy.generated
    value_dict["Highest generation in a period"] = high_period
    daily_data = aggregate(all_raw_data, period_length=timedelta(days=1))
    sorted_data = sorted(daily_data, key=lambda x: x.generated)
    highest_day = sorted_data[-1]
    value_dict["Highest generation in a day"] = highest_day.energy.generated
    lowest_day = sorted_data[0]
    value_dict["Lowest generation in a day"] = lowest_day.energy.generated

    return value_dict


def graphs():
    """ Function that generates some interesting graphs from the data """
    data_dict = {}
    hdb = Hybrid(debug=False)

    twodaysago = get_current_datetime() - timedelta(days=2)
    mine = hdb.get_power(start=twodaysago)
    data_dict["Last two day's figures"] = mine
    for title, chartdata in data_dict.items():
        chart(chartdata, title=title)

    data_dict["All-time"] = hdb.get_power()
    one_day = timedelta(days=1)
    data_dict["All-time by day"] = aggregate(data_dict["All-time"],
                                             period_length=one_day)

    # Average generation by day of year
    for title, chartdata in data_dict.items():
        chart(chartdata, title=title)

    # Average generation by time of day
    # Average consumption by time of day


if __name__ == "__main__":
    main()
