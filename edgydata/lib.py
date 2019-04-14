def batch(iterable, size):
    mylist = sorted(iterable)
    lenlist = len(mylist)
    for ndx in range(0, lenlist, size):
        yield mylist[ndx:min(ndx + size, lenlist)]
