import os
import sys
from itertools import chain
import json
import sys
import logging

import ghost

sys.path.append(os.path.abspath('.'))

from scrapecat import models

from scrapecat import models, utils


from scrapecat import models, utils, validators
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
        self.body = self.ghost.main_frame.findFirstElement('body')
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
        els = utils.traverse(self.body,
                match_el=lambda el: utils.find_emails(el.attribute('href')),
                match_text=lambda s: utils.find_emails(s), ignore_tags=[])
        return list(chain(*[utils.find_emails(el.attribute('href')) + utils.find_emails(el.toPlainText()) for el in els]))

    def phone_numbers(self):
        number_match = lambda t: list(phonenumbers.PhoneNumberMatcher(t, 'US'))
        els = utils.traverse(self.body,
                match_text=number_match)
        return list(chain(*[[match.raw_string for match in phonenumbers.PhoneNumberMatcher(el.toPlainText(), 'US')] for el in els]))

if __name__ == '__main__':
    url = sys.argv[1]
    c = ContactPlugin(url=url)
    print json.dumps(c.process())
