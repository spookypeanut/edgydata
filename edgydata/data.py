from datetime import date


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


class Usage(object):
    """ An object that represents a single entry of electricity generation /
    usage data.
    """
    def __init__(self, start_time, duration, generated, consumed, imported,
                 exported, self_consumed):
        self.start_time = start_time
        self.duration = duration
        self.generated = generated
        self.consumed = consumed
        self.imported = imported
        self.exported = exported
        self.self_consumed = self_consumed

    def __repr__(self):
        return "<Usage for %s minutes from %s>" % (self.duration,
                                                   self.start_time)
