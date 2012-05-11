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
        self.email_els, emails = self.emails()
        self.phone_els, phones = self.phones()
        contacts = self.contacts()

        return {
            'emails' : emails,
            'phones' : phones,
            'contacts': contacts,
        }

    def emails(self, parent=None):
        email_els = utils.traverse(parent or self.body,
                match_el=lambda el: utils.find_emails(el.attribute('href')),
                match_text=lambda s: utils.find_emails(s), ignore_tags=[])
        return email_els, list(set(chain(*[utils.find_emails(el.attribute('href')) + utils.find_emails(unicode(el.toPlainText())) for el in email_els])))

    def phones(self, parent=None):
        number_match = lambda t: list(phonenumbers.PhoneNumberMatcher(t, 'US'))
        phone_els = utils.traverse(parent or self.body,
                match_text=number_match)
        phones = []
        for el in phone_els:
            for match in phonenumbers.PhoneNumberMatcher(unicode(el.toPlainText()), 'US'):
                phones.append({
                        'type' : utils.number_type(unicode(el.toPlainText()), match.raw_string),
                        'number' : match.raw_string
                    })
        return phone_els, phones

    def contacts(self):
        group_result = utils.group_by_common_parents(self.email_els, self.phone_els)
        doc = self.body.document()

        results = []

        for path, els in utils.find_similar_selector_paths([group_parent for email, phone, group_parent in group_result]):
            for group_parent in utils.get_elements_for_path(doc, path):
                email_els, emails = self.emails(group_parent)
                phone_els, phones = self.phones(group_parent)
                result = {
                    'emails': emails,
                    'phones': phones,
                    'addresses': list(chain(*[
                        [(lambda city, state, zip_code: {'city': city.strip(), 'state': state, 'zip': zip_code})(*match) for match in matches]
                            for el, matches in utils.traverse_extract(group_parent, match_text=lambda s: validators.address_re.findall(s))
                    ])),
                    'urls': list(set([a.attribute('href') for a in group_parent.findAll('a') if validators.url_no_path_re.match(a.attribute('href'))])),
                    'social_urls': dict([([name for name in validators.social_url_re.match(a.attribute('href')).groups() if name][0], a.attribute('href')) for a in group_parent.findAll('a') if validators.social_url_re.match(a.attribute('href'))]),
                }
                if any(result.values()):
                    results.append(result)
        return results

if __name__ == '__main__':
    url = sys.argv[1]
    c = ContactPlugin(url=url)
    print json.dumps(c.process())
