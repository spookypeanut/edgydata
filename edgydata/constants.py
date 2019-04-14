from enum import Enum

POWER_TYPES = set(['self_consumed', 'generated', 'imported', 'consumed',
                   'exported'])
POWER = Enum("power", " ".join(sorted(POWER_TYPES)))

SE_DATE_FORMAT = "%Y-%m-%d"
SE_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class DatePreset(Enum):
    DAY = 1
    WEEK = 2
    MONTH = 3
    YEAR = 4


class Combiners(Enum):
    SUM = 1
    MEAN = 2
    MIN = 3
    MAX = 4
    SPECIFIC = 5
