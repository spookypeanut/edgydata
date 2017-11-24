import time


class Abstract(object):
    """ An abstract class that the remote, local and hybrid dbs can inherit
    from. This doesn't contain a lot as there is little overlap between all
    three.
    """
    def __init__(self, debug=True):
        self._debug = debug

    def debug(self, msg):
        if not self._debug:
            return
        print("[%s] %s" % (time.asctime(), msg))
