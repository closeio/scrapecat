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

class ContactsPlugin(Plugin):
    def process(self):
        return {
            'emails': None,
            'phones': None,
            'contacts': None,
        }

    def emails(self):
        self.email_els = utils.traverse(self.body,
                match_el=lambda el: utils.find_emails(el.attribute('href')),
                match_text=lambda s: utils.find_emails(s), ignore_tags=[])
        return list(set(chain(*[utils.find_emails(el.attribute('href')) + utils.find_emails(unicode(el.toPlainText())) for el in self.email_els])))


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


