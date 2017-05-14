from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def date_from_string(input_string):
    return datetime.strptime(input_string,).date()


def datetime_from_string(input_string):
    raise NotImplementedError


def date_to_string(input_date):
    return input_date.strftime(DATE_FORMAT)


def datetime_to_string(input_datetime):
    return input_datetime.strftime(DATETIME_FORMAT)
