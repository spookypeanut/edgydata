"""
Ways to visualise a data set:
    Single value (Maximum, minimum, mean, median)
    Line graph
"""
import matplotlib.pyplot as pyplot


def _pyplot(input_data, only_show, output_file):
    X = range(10)
    pyplot.plot(X, [x*x for x in X])
    pyplot.show()

CHART_TYPES = {"pyplot": _pyplot}


def chart(input_data, chart_type=list(CHART_TYPES)[0], only_show=None,
          output_file=None):
    chart_callable = CHART_TYPES[chart_type]
    return chart_callable(input_data, only_show, output_file)
