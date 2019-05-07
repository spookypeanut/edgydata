from edgydata.backend.abstract import Abstract as AbstractBE
from edgydata.backend.remote import Remote as RemoteBE
from edgydata.backend.local import Local as LocalBE
from edgydata.time import (get_current_datetime, get_midnight_after,
                           get_midnight_before)


class Hybrid(AbstractBE):
    """ All of the solar power data, stored in a local database. If what's
    requested is not in there, it's retrieved from the remote (and then stored
    locally)
    """

    def __init__(self, api_key=None, local_path=None, debug=False):
        AbstractBE.__init__(self, debug=debug)
        self._remote_be = RemoteBE(api_key=api_key, debug=debug)
        self._local_be = LocalBE(path=local_path, debug=debug)
        if not self._local_be.is_present():
            self._local_be.create()

    def get_power(self, site_id=None, start=None, end=None):
        msg = "All datetimes must have a timezone"
        if start is not None and (start.tzinfo is None or
                                  start.tzinfo.utcoffset(start) is None):
            raise ValueError(msg)
        if end is not None and (end.tzinfo is None or
                                end.tzinfo.utcoffset(end) is None):
            raise ValueError(msg)
        min_local, max_local = self._local_be.get_time_limits(site_id=site_id)
        if start is not None and end is not None:
            if min_local < start and max_local > end:
                return self._local_be.get_power(site_id=site_id,
                                                start=start, end=end)
        self._update_power(site_id=site_id, start=start, end=end)
        return self._local_be.get_power(site_id=site_id, start=start, end=end)

    def _update_power(self, site_id=None, start=None, end=None):
        now = get_current_datetime()
        # Let's get a round number of days, just to make things cleaner
        if start is not None:
            start = get_midnight_before(start)
        if end is not None:
            end = get_midnight_after(end)
            # Don't get imcomplete days
            if end > now:
                end = get_midnight_before(end)
        min_loc, max_loc = self._local_be.get_time_limits(site_id=site_id)
        min_rem, max_rem = self._remote_be.get_time_limits(site_id=site_id)
        retrieved = []
        if start is None or start < min_loc:
            self.debug("Getting from %s to %s" % (start, min_loc))
            pp = self._remote_be.get_power(site_id=site_id,
                                           start=start, end=min_loc)
            retrieved.extend(pp)
        # if min_loc is None and start is None, we already have
        # everything there is to get
        if (end is None or end > max_loc) and not \
                (min_loc is None and start is None):
            self.debug("Getting from %s to %s" % (max_loc, end))
            pp = self._remote_be.get_power(site_id=site_id,
                                           start=max_loc, end=end)
            retrieved.extend(pp)
        if retrieved:
            self._local_be.add_power(retrieved)

    def get_site(self, site_id):
        try:
            site = self._local_be.get_site(site_id=site_id)
        except Exception:
            site = self._remote_be.get_site(site_id=site_id)
            self._local_be.add_site(site)
        return site

    def get_site_ids(self):
        # I can't think of a better way to do this
        return self._remote_be.get_site_ids()
