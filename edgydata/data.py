from __future__ import division, print_function

from datetime import date
from edgydata.constants import POWER_TYPES


class Site(object):
    """ An object that represents one of the solar generation sites returned by
    the SolarEdge API. While peak_power can be given, it doesn't have to be
    (since it can sort of be deduced from the rest of the data).
    """
    # If you add an attribute, make sure you add it here...
    _types = {"site_id": int, "name": str, "start_date": date,
              "end_date": date, "peak_power": float, "country": str,
              "timezone": str}

    def __init__(self, **kwargs):
        for eachattr in self.list_attrs():
            if eachattr not in kwargs:
                msg = "Site needs to be initialized with %s"
                raise AttributeError(msg % eachattr)
            setattr(self, eachattr, kwargs[eachattr])

    @classmethod
    def list_attrs(cls):
        return sorted(cls._types.keys())

    @classmethod
    def attr_types(cls):
        return cls._types

    def __eq__(self, other):
        for attr in self.list_attrs():
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True


class Energy(dict):
    def __init__(self, **kwargs):
        for eachtype in POWER_TYPES:
            if eachtype not in kwargs:
                msg = "%s not provided: expected all of %s"
                raise ValueError(msg % (eachtype, POWER_TYPES))
        dict.__init__(self, **kwargs)

    def __getattr__(self, name):
        if name in POWER_TYPES:
            return self[name]
        dict.__getattr(self, name)

    def __add__(self, other):
        kwargs = {}
        for eachtype in POWER_TYPES:
            kwargs[eachtype] = self[eachtype] + other[eachtype]
        return Energy(**kwargs)


class PowerPeriod(object):
    """ An object that represents a single entry of electricity generation /
    usage data.
    The default is average POWER (kW) over the power period. To convert to
    energy (kWh), use PowerPeriod.energy
    """
    def __init__(self, site_id, start_time, duration, **kwargs):
        self.site_id = site_id
        self.start_time = start_time
        self.duration = duration
        for eachtype in POWER_TYPES:
            if eachtype not in kwargs:
                msg = "%s not provided: expected all of %s"
                raise ValueError(msg % (eachtype, POWER_TYPES))
            setattr(self, eachtype, kwargs[eachtype])

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
        return Energy(**energydict)

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
        return other.__lt__(self)

    def __eq__(self, other):
        if self.start_time != other.start_time:
            return False
        for eachtype in sorted(self._types()):
            if getattr(self, eachtype) != getattr(other, eachtype):
                return False
        return True

    def __radd__(self, other):
        return self.__add__(other)

    def __add__(self, other):
        if isinstance(other, int):
            if other == 0:
                return self
            msg = "Can't add a PowerPeriod (%s) to an int (%s)"
            raise ValueError(msg % (self, other))
        if self == other:
            raise ValueError("Can't add a PowerPeriod to itself")
        if self.start_time == other.start_time:
            msg = "These two start at the same time: %s"
            raise ValueError(msg % self.start_time)
        elif self.start_time < other.start_time:
            a = self
            b = other
        else:
            a = other
            b = self
        if not a.site_id == b.site_id:
            raise ValueError("These two PowerPeriods are for different sites")
        start_time = a.start_time
        if a.start_time + a.duration == b.start_time:
            duration = a.duration + b.duration
        else:
            print("Warning: These two PowerPeriods are not consecutive")
            print(a)
            print(b)
            duration = (b.start_time - a.start_time) + b.duration
        mytypes = {"start_time": start_time, "duration": duration,
                   "site_id": a.site_id}
        for type_ in self._types():
            # Remember, these contain an average power, so we have
            # average the two numbers
            mytypes[type_] = (getattr(a, type_) + getattr(b, type_)) / 2
        result = PowerPeriod(**mytypes)
        return result

    def __repr__(self):
        hours = 24 * self.duration.days + self.duration.seconds / 60 / 60
        return "<PowerPeriod for %sh from %s>" % (hours, self.start_time)
