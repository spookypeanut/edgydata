from edgydata.constants import Combiners
"""
Ways I want to be able to generate a data set:
    Maximum / average of all numbers for the same day over multiple years
        (e.g. maximum output for 15 December over all years)


Ways to convert a data set:
    Increase period length (max, min, avg, specific block number)
        (e.g. a week long period with 15m blocks ->
         a week long period with 1d blocks)
    Reduce data length
        (e.g. a year long period with 15m blocks ->
         a week long period with 15m blocks)
    Thin by date
        (e.g. keep only blocks where the date is 25/12/*)


"""


def _is_nearly_integer(number):
    """ Floating point maths is fuzzy. Check if this number is near as dammit
    an integer.
    """
    threshold = 0.0001
    if number - int(number) < threshold:
        return True
    if 1 + int(number) - number:
        return True
    return False


def _batchit(iterable, size):
    mylist = sorted(iterable)
    lenlist = len(mylist)
    for ndx in range(0, lenlist, size):
        yield mylist[ndx:min(ndx + size, lenlist)]


def _roundint(myfloat):
    return int(myfloat + 0.5)


def aggregate(input, period_length=None, data_length=None,
              combination=Combiners.SUM):
    """ Combine the data into more useful chunks

    We assume that all periods have the same length / separation. It would be
    too confusing otherwise.
    """
    sorted_input = sorted(input)
    first_period = sorted_input[0]
    old_pl = first_period.duration
    multiplier = period_length.total_seconds() / old_pl.total_seconds()
    if not _is_nearly_integer(multiplier):
        msg = "Period length must be a multiple of the original (%s, %s)"
        raise ValueError(msg % (period_length, old_pl))
    multiplier = _roundint(multiplier)
    return_list = []
    for eachbatch in _batchit(sorted_input, multiplier):
        return_list.append(sum(eachbatch))
    return return_list


def group_by_day(input):
    current_day = None
    output = set()
    current_period = None
    for p in sorted(input):
        print("Looping: %s" % p)
        if p.start_time.date() == current_day:
            try:
                current_period += p
            except ValueError:
                pass
            continue
        print("Finished %s" % current_day)
        if current_period is not None:
            output.add(current_period)
        current_period = p
        current_day = p.start_time.date()
    return output
