class Site(object):
    """ An object that represents one of the solar generation sites returned by
    the SolarEdge API. While the peak_power and lifetime_energy can be given,
    they don't have to be (since they can be deduced from the rest of the
    data).
    """
    def __init__(self, site_id, start_date, end_date,
                 peak_power=0, lifetime_energy=0):
        self.site_id = site_id
        self.start_date = start_date
        self.end_date = end_date
        self.peak_power = peak_power
        self.lifetime_energy = lifetime_energy


class Usage(object):
    """ An object that represents a single entry of electricity generation /
    usage data.
    """
    def __init__(self, start_time, duration, imported, exported, self_used):
        self.start_time = start_time
        self.duration = duration
        self.imported = imported
        self.exported = exported
        self.self_used = self_used
