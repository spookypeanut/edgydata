from edgydata.data import Site

class Remote(object):
    def __init__(self, api_key):
        self._api_key = api_key

    def _get_site_ids(self):
        """ Get all the site ids of all the sites connected with this SolarEdge
        account
        """
        pass

    def get_sites(self):
        """ Return Site objects for all the sites connected with this SolarEdge
        account
        """
        for site_id in self._get_site_ids():
            yield self.get_site(site_id)

    def get_site(self, site_id):
        """ Return a Site object from a given site id, by querying the details
        from the SolarEdge API
        """
        pass
