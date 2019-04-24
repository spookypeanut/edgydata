from datetime import datetime, timedelta
import pytz

from edgydata.constants import SE_DATE_FORMAT, SE_DATETIME_FORMAT


def date_to_datetime(input_, timezone="UTC"):
    """ Convert a date into a datetime (midnight) """
    naive = datetime.combine(input_, datetime.min.time())
    utc_datetime = pytz.utc.localize(naive)
    if timezone == "UTC":
        return utc_datetime
    tz_object = pytz.timezone(timezone)
    return utc_datetime.astimezone(tz_object)


def datetime_to_int(mytime):
    """ Convert a datetime.datetime object to a unix timestamp. """
    # First, see if we have been given a tz naive datetime
    epoch_time = datetime(1970, 1, 1)
    try:
        return int((mytime - epoch_time).total_seconds())
    except TypeError:
        # If not, epoch_time is relative to utc
        epoch_time = pytz.utc.localize(epoch_time)
        return int((mytime - epoch_time).total_seconds())


def date_to_int(mydate):
    """ Convert a datetime.date object to a unix timestamp """
    return datetime_to_int(datetime.combine(mydate, datetime.min.time()))


def timedelta_to_int(mytimedelta):
    return mytimedelta.seconds


def int_to_timedelta(myint):
    return timedelta(seconds=myint)


def int_to_datetime(myint, timezone="UTC"):
    """ Convert a unix timestamp to a datetime.datetime object """
    naive = datetime.utcfromtimestamp(myint)
    utc_datetime = pytz.utc.localize(naive)
    if timezone == "UTC":
        return utc_datetime
    tz_object = pytz.timezone(timezone)
    return utc_datetime.astimezone(tz_object)


def int_to_date(myint, timezone="UTC"):
    """ Convert a unix timestamp to a datetime.date object """
    return int_to_datetime(myint, timezone=timezone).date()


def date_to_string(input_date):
    return input_date.strftime(SE_DATE_FORMAT)


def string_to_date(input_string, timezone="UTC"):
    naive = datetime.strptime(input_string, SE_DATE_FORMAT)
    tz_object = pytz.timezone(timezone)
    return tz_object.localize(naive).date()


def datetime_to_string(input_datetime):
    return input_datetime.strftime(SE_DATETIME_FORMAT)


def string_to_datetime(input_string, timezone="UTC"):
    naive = datetime.strptime(input_string, SE_DATETIME_FORMAT)
    tz_object = pytz.timezone(timezone)
    return tz_object.localize(naive)


def get_current_datetime():
    return datetime.utcnow().replace(tzinfo=pytz.utc)


def get_midnight_before(time):
    return time.replace(hour=0, minute=0, second=0, microsecond=0)


def get_midnight_after(time):
    before = get_midnight_before(time)
    return before + timedelta(days=1)
