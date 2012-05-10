import sys
import logging
import ghost
from scrapecat import models, utils
from PySide.QtWebKit import QWebSettings

import phonenumbers

class Plugin(object):
    def __init__(self, *args, **kwargs):
        logging.debug('Starting __init__')
        self.url = kwargs['url']
        self.ghost = ghost.Ghost(wait_timeout=60)
        logging.debug('Created Ghost object')

        QWebSettings.globalSettings().setAttribute(QWebSettings.AutoLoadImages, False)
        QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, False)
        self.page, self.resources = self.ghost.open(self.url)
        logging.debug('Fetched the page')

    def process(self, webpage):
        raise NotImplemented


class BasePlugin(Plugin):
    pass

class ContactPlugin(Plugin):
    def process(self):
        return {
            'emails' : self.emails(),
            'phone_numbers' : self.phone_numbers()
        }

    def emails(self):
        els = utils.traverse(self.ghost.main_frame.findFirstElement('body'),
                match_el=lambda el: '@' in el.attribute('href'))
        return [el.attribute('href').replace('mailto:', '') for el in els]

    def phone_numbers(self):
        number_match = lambda t: list(phonenumbers.PhoneNumberMatcher(t, 'US'))
        els = utils.traverse(self.ghost.main_frame.findFirstElement('body'),
                match_text=number_match)
        return [el.toPlainText() for el in els]

if __name__ == '__main__':
    url = sys.argv[1]
    c = ContactPlugin(url=url)
    print json.dumps(c.process())
