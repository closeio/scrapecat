import os
import sys
from itertools import chain
import json
import sys
import logging

import ghost

sys.path.append(os.path.abspath('.'))


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
        self.frame = self.ghost.main_frame
        self.body = self.ghost.main_frame.findFirstElement('body')
        logging.debug('Fetched the page')

    def process(self, webpage):
        raise NotImplemented


class BasePlugin(Plugin):
    def process(self):
        # This will ignore multiple instances of the same meta tag.
        meta = dict([(el.attribute('name'), el.attribute('content')) for el in self.frame.findAllElements('meta')])
        title = self.frame.findFirstElement('title').toPlainText()
        return {
            'meta': meta,
            'title': title,
        }

class ContactPlugin(Plugin):
    def process(self):
        emails = self.emails()
        phones = self.phones()
        contacts = self.contacts()

        return {
            'emails' : emails,
            'phones' : phones,
            'contacts': contacts,
        }

    def emails(self):
        self.email_els = utils.traverse(self.body,
                match_el=lambda el: utils.find_emails(el.attribute('href')),
                match_text=lambda s: utils.find_emails(s), ignore_tags=[])
        return list(set(chain(*[utils.find_emails(el.attribute('href')) + utils.find_emails(el.toPlainText()) for el in self.email_els])))

    def phones(self):
        number_match = lambda t: list(phonenumbers.PhoneNumberMatcher(t, 'US'))
        self.phone_els = utils.traverse(self.body,
                match_text=number_match)
        return list(set(chain(*[[utils.format_us_phone_number(match.raw_string) for match in phonenumbers.PhoneNumberMatcher(el.toPlainText(), 'US')] for el in self.phone_els])))

    def contacts(self):
        return [{
            'emails': list(set(utils.find_emails(email.attribute('href')) + utils.find_emails(email.toPlainText()))),
            'phones': list(set([utils.format_us_phone_number(match.raw_string) for match in phonenumbers.PhoneNumberMatcher(phone.toPlainText(), 'US')])),
            'addresses': [
                [(lambda city, state, zip_code: {'city': city.strip(), 'state': state, 'zip': zip_code})(*match) for match in matches]
                    for el, matches in utils.traverse_extract(group_parent, lambda s: validators.address_re.findall(s))
            ],
        } for email, phone, group_parent in utils.group_by_common_parents(self.email_els, self.phone_els)]

if __name__ == '__main__':
    url = sys.argv[1]
    c = ContactPlugin(url=url)
    print json.dumps(c.process())
