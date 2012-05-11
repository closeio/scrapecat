from bs4 import BeautifulSoup

class Plugin(object):
    def __init__(self, webpage):
        assert webpage
        self.webpage = webpage
        self.bs = BeautifulSoup(self.webpage['html']) 

    def process(self):
        raise NotImplemented


class BasePlugin(Plugin):
    def process(self):
        meta = dict([(tag.attrs['name'], tag.attrs['content']) for tag in self.bs.head.find_all('meta')])
        print "meta ", meta
        title = self.bs.title.string
        print "title ", title
        return {
            'url': self.webpage['url'],
            'meta': meta,
            'title': title,
            'http_headers': self.webpage['headers'],
        }


class PluginProcessor(object):

    def __init__(self, *args, **kwargs):
        self.registry = {'base': BasePlugin}
        self.pipeline = []
        self.response = {}

    def register(self, name, cls):
        assert name and cls and isinstance(cls, Plugin)
        self.registry[name] = cls

    def init(self, webpage):
        for name, plugin_cls in self.registry.items():
            self.pipeline.append((name, plugin_cls(webpage)))

    def process(self):
        for name, plugin in self.pipeline:
            self.response[name] = plugin.process()

        return self.response


