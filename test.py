""" A script created to test the edgydata database, but in doing so also
provide some interesting data
"""

from datetime import datetime, timedelta
from edgydata.backend.hybrid import Hybrid
from edgydata.visualize import chart
from edgydata.aggregate import aggregate


def main():
    """ Generate some interesting information about the data """
    values()
    graphs()


def values():
    """ Function that generates some interesting values from the data """
    # Examples of values to get:
    # Lowest generation in a day
    # Highest generation in a day
    # Day of the year that gives the lowest average generation
    # Day of the year that gives the highest average generation
    value_dict = {}
    hdb = Hybrid(debug=True)
    all_raw_data = hdb.get_power()
    highest_period = sorted(all_raw_data, key=lambda x: x.generated)[-1]
    value_dict["Highest generation in a period"] = highest_period.generated
    daily_data = aggregate(all_raw_data, period_length=timedelta(days=1))
    highest_day = sorted(daily_data, key=lambda x: x.generated)[-1]
    value_dict["Highest generation in a day"] = highest_day.generated

    print(value_dict)


def graphs():
    """ Function that generates some interesting graphs from the data """
    data_dict = {}
    hdb = Hybrid(debug=True)

    twodaysago = datetime.now() - timedelta(days=2)
    mine = hdb.get_power(start=twodaysago)
    data_dict["Last two day's figures"] = mine
    for title, chartdata in data_dict.items():
        chart(chartdata, title=title)
    # Average generation by day of year
    # Average generation by time of day
    # Average consumption by time of day


if __name__ == "__main__":
    main()
