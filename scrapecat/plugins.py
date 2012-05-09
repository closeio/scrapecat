from scrapecat import models


"""
"""
class Plugin(object):
    def __init__(self, *args, **kwargs):
        pass

    def process(self, webpage):
        raise NotImplemented


"""
"""
class BasePlugin(Plugin):
    pass


"""
"""
class ContactPlugin(Plugin):
    pass
