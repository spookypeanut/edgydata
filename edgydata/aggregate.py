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

Ways to visualise a data set:
    Single value (Maximum, minimum, mean, median)
    Line graph

"""


def aggregate(input, period_length=15, separation=15, combination=sum):
    """ Combine the data into more useful chunks
    """


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
