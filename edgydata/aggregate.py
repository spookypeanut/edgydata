"""
Ways I want to be able to generate a data set:
    Maximum / average of all numbers for the same day over multiple years
        (e.g. maximum output for 15 December over all years)


Ways to convert a data set:
    Increase period length (max, min, avg, specific block number)
        (e.g. a week long period with 15m blocks ->
         a week long period with 1d blocks, or
         all periods with 15m blocks ->
         all periods with one month blocks)
    Reduce data length
        (e.g. a year long period with 15m blocks ->
         a week long period with 15m blocks)
    Thin by date
        (e.g. keep only blocks where the date is 25/12/*)
    Combine by date
        (e.g. average all periods by month
         sum all periods by day of week)


"""
from __future__ import print_function

from collections import Counter
from edgydata.constants import Combiners
from edgydata.lib import batch


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


def _has_duplicate_times(iterable):
    start_time_list = [a.start_time for a in iterable]
    if len(start_time_list) == len(set(start_time_list)):
        return False
    print("Found duplicates")
    dups = [t for t in Counter(start_time_list).items() if t[1] > 1]
    print(dups)
    start_time, _ = dups[0]
    mylist = [a for a in iterable if a.start_time == start_time]
    for pp in mylist:
        print(pp)
        print(pp.consumed)
        print(pp.exported)
    return True


def _roundint(myfloat):
    return int(myfloat + 0.5)


def combine_periods(power_periods, combiner):
    if combiner == Combiners.SUM:
        return sum(power_periods)
    if combiner == Combiners.MEAN:
        return sum(power_periods) / len(power_periods)
    raise NotImplementedError


def aggregate(input_, period_length=None, data_length=None,
              combination=Combiners.SUM):
    """ Combine the data into more useful chunks

    We assume that all periods have the same length / separation. It would be
    too confusing otherwise.
    """
    sorted_input = sorted(input_)
    first_period = sorted_input[0]
    old_pl = first_period.duration
    multiplier = period_length.total_seconds() / old_pl.total_seconds()
    if not _is_nearly_integer(multiplier):
        msg = "Period length must be a multiple of the original (%s, %s)"
        raise ValueError(msg % (period_length, old_pl))
    multiplier = _roundint(multiplier)
    return_list = []
    if _has_duplicate_times(sorted_input):
        raise ValueError
    for eachbatch in batch(sorted_input, multiplier):
        try:
            total = combine_periods(eachbatch, combination)
        except ValueError:
            print(eachbatch)
            raise
        return_list.append(total)
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
