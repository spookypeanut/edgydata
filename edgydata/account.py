from edgydata.base import AbstractSolarEdge, BASE_URL
from edgydata.site import Site

class Account(AbstractSolarEdge):
    def get_site_ids(self):
        url = "%s/sites/list" % BASE_URL
        data = self._raw_call(url, {})
        ids = [a["id"] for a in data["sites"]["site"]]
        # Return this as a list, in the same order as the API gives them
        return ids

    def get_sites(self):
        return [Site(self._api_key, id_) for id_ in self.get_site_ids()]
