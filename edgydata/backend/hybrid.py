from edgydata.backend.abstract import Abstract as AbstractBE
from edgydata.backend.remote import Remote as RemoteBE
from edgydata.backend.local import Local as LocalBE

from datetime import timedelta


def get_midnight_before(time):
    return time.replace(hour=0, minute=0, second=0, microsecond=0)


def get_midnight_after(time):
    before = get_midnight_before(time)
    return before + timedelta(days=1)


class Hybrid(AbstractBE):
    """ All of the solar power data, stored in a local database. If what's
    requested is not in there, it's retrieved from the remote (and then stored
    locally)
    """

    def __init__(self, api_key=None, local_path=None, debug=True):
        AbstractBE.__init__(self, debug=debug)
        self._remote_be = RemoteBE(api_key=api_key)
        self._local_be = LocalBE(path=local_path)

    def get_power(self, site_id=None, start=None, end=None):
        min_local, max_local = self._local_be.get_time_limits(site_id=site_id)
        if start is not None and end is not None:
            if min_local < start and max_local > end:
                return self._local_be.get_power(site_id=site_id,
                                                start=start, end=end)
        self._update_power(site_id=site_id, start=start, end=end)
        return self._local_be.get_power(site_id=site_id, start=start, end=end)

    def _update_power(self, site_id=None, start=None, end=None):
        min_loc, max_loc = self._local_be.get_time_limits(site_id=site_id)
        min_rem, max_rem = self._remote_be.get_time_limits(site_id=site_id)
        retrieved = []
        if start is None or start < min_loc:
            pp = self._remote_be.get_power(site_id=site_id,
                                           start=start, end=min_loc)
            retrieved.extend(pp)
        if end is None or end > max_loc:
            pp = self._remote_be.get_power(site_id=site_id,
                                           start=max_loc, end=end)
            retrieved.extend(pp)
        self._local_be.add_power(retrieved)
