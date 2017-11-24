from edgydata.backend.abstract import Abstract as AbstractBE
from edgydata.backend.remote import Remote as RemoteBE
from edgydata.backend.local import Local as LocalBE


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
        raise NotImplementedError
