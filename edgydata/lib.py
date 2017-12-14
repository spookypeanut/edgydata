from datetime import datetime

def date_to_datetime(input):
    return datetime.combine(input, datetime.min.time())
