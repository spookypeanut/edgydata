from datetime import date
from edgydata.constants import POWER_TYPES


class Site(object):
    """ An object that represents one of the solar generation sites returned by
    the SolarEdge API. While peak_power can be given, it doesn't have to be
    (since it can sort of be deduced from the rest of the data).
    """
    # If you add an attribute, make sure you add it here...
    _types = {"site_id": int, "name": str, "start_date": date, "end_date": date,
              "peak_power": float}

    def __init__(self, site_id, name, start_date, end_date, peak_power=0):
        # ... and here
        self.site_id = site_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.peak_power = peak_power

    @classmethod
    def list_attrs(cls):
        return sorted(cls._types.keys())

    @classmethod
    def attr_types(cls):
        return cls._types


class PowerPeriod(object):
    """ An object that represents a single entry of electricity generation /
    usage data.
    The default is average POWER (kW) over the power period. To convert to
    energy (kWh), use PowerPeriod.energy
    """
    def __init__(self, site_id, start_time, duration, generated, consumed,
                 imported, exported, self_consumed):
        self.site_id = site_id
        self.start_time = start_time
        self.duration = duration
        self.generated = generated
        self.consumed = consumed
        self.imported = imported
        self.exported = exported
        self.self_consumed = self_consumed

    @classmethod
    def _types(cls):
        # Should already be a set, but this is a cheap way to make a
        # copy of it
        return set(POWER_TYPES)

    @property
    def energy(self):
        energydict = {}
        for eachtype in self._types():
            # To convert from average kW to kWh
            hours = self.duration.seconds / 60 / 60
            energydict[eachtype] = getattr(self, eachtype) * hours
        return energydict

    def __lt__(self, other):
        if self.start_time < other.start_time:
            return True
        elif self.start_time > other.start_time:
            return False
        for eachtype in sorted(self._types()):
            if getattr(self, eachtype) < getattr(other, eachtype):
                return True
            if getattr(self, eachtype) > getattr(other, eachtype):
                return False
        return False

    def __gt__(self, other):
        if self.__lt__(other) or self.__eq__(other):
            return False
        return True

    def __eq__(self, other):
        if self.start_time != other.start_time:
            return False
        for eachtype in sorted(self._types()):
            if getattr(self, eachtype) != getattr(other, eachtype):
                return False
        return True

    def __add__(self, other):
        if self.start_time < other.start_time:
            a = self
            b = other
        else:
            a = other
            b = self
        duration = a.duration + b.duration
        start_time = a.start_time
        mytypes = {"start_time": start_time, "duration": duration}
        for type_ in self._types():
            mytypes[type_] = getattr(a, type_) + getattr(b, type_)
        return PowerPeriod(**mytypes)

    def __repr__(self):
        hours = 1.0 * self.duration.seconds / 60 / 60
        return "<PowerPeriod for %sh from %s>" % (hours, self.start_time)
