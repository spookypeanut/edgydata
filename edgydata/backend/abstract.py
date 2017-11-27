from abc import ABCMeta, abstractmethod
import time


class Abstract(object):
    """ An abstract class that the remote, local and hybrid dbs can inherit
    from. This doesn't contain a lot as there is little overlap between all
    three.
    """
    __metaclass__ = ABCMeta

    def __init__(self, debug=True):
        self._debug = debug

    def debug(self, msg):
        if not self._debug:
            return
        print("[%s] %s" % (time.asctime(), msg))

    @abstractmethod
    def get_power(self, site_id, start, end):
        """ Get the list of PowerPeriod assets that cover the time period
        from start to end.
        """
        return

    @abstractmethod
    def get_site(self, site_id):
        """ Get information about a site. """

    @abstractmethod
    def get_site_ids(self):
        """ Get all the site ids of all the sites.
        """

    def get_sites(self):
        """ Return Site objects for all the sites.
        """
        for site_id in self.get_site_ids():
            yield self.get_site(site_id)
