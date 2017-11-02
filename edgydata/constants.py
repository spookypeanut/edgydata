from enum import Enum

POWER_TYPES = ['self_consumed', 'generated', 'imported', 'consumed', 'exported']
POWER = Enum("usage", " ".join(POWER_TYPES))
