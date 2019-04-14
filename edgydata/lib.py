from datetime import datetime


def date_to_datetime(input):
    return datetime.combine(input, datetime.min.time())


def batch(iterable, size):
    mylist = sorted(iterable)
    lenlist = len(mylist)
    for ndx in range(0, lenlist, size):
        yield mylist[ndx:min(ndx + size, lenlist)]
