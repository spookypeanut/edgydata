"""
Ways to visualise a data set:
    Single value (Maximum, minimum, mean, median)
    Line graph
"""
import matplotlib.pyplot as pyplot
from edgydata.constants import POWER_TYPES


def _pyplot(input_data, only_show, output_file):
    sorted_data = sorted(input_data)
    X = [pp.start_time for pp in sorted_data]
    for eachtype in POWER_TYPES:
        if only_show is not None and eachtype not in only_show:
            continue
        series = [pp.energy[eachtype] for pp in sorted_data]
        pyplot.plot(X, series)
    pyplot.show()

CHART_TYPES = {"pyplot": _pyplot}


def chart(input_data, chart_type=list(CHART_TYPES)[0], only_show=None,
          output_file=None):
    chart_callable = CHART_TYPES[chart_type]
    return chart_callable(input_data, only_show, output_file)
