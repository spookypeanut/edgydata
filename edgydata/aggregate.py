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
