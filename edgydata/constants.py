from enum import Enum

POWER_TYPES = set(['self_consumed', 'generated', 'imported', 'consumed',
                   'exported'])
POWER = Enum("power", " ".join(sorted(POWER_TYPES)))
