import sys
import logging
import ghost

import phonenumbers

class Plugin(object):
    def __init__(self, *args, **kwargs):
        logging.debug('Starting __init__')
        self.url = kwargs['url']
        self.ghost = ghost.Ghost(wait_timeout=60)
        logging.debug('Created Ghost object')
        self.page, self.resources = self.ghost.open(self.url)
        logging.debug('Fetched the page')

    def process(self, webpage):
        raise NotImplemented

    def traverse(self, parent_node, match_el=None, match_text=None, depth=0):
        ret = []
        node_info = parent_node.evaluateJavaScript(
                '''(function(el) {
                    var ret = []; el = el.firstChild;
                    while (el) {
                        ret.push([el.nodeType, el.nodeValue]);
                        el = el.nextSibling;
                    } return ret;
                })(this);''')
        if match_el and match_el(parent_node):
            ret.append(parent_node)
        if node_info:
            node = parent_node.firstChild()
            for node_type, node_value in node_info:
                  if node_type == 1: # element node
                      ret += self.traverse(node,
                              match_el=match_el,
                              match_text=match_text,
                              depth=depth+1)
                      # print ' '*depth, 'NODE', node.tagName()
                      node = node.nextSibling()
                  elif node_type == 3: # text node
                      stripped_node_value = node_value.strip()
                      if stripped_node_value: # skip empty nodes
                              if match_text and match_text(stripped_node_value):
                                  ret.append(parent_node)
                              # print ' '*depth, 'TEXT', stripped_node_value
        return ret

class BasePlugin(Plugin):
    pass

class ContactPlugin(Plugin):
    def process(self):
        return {
            'emails' : self.emails(),
            'phone_numbers' : self.phone_numbers()
        }

    def emails(self):
        els = self.traverse(self.ghost.main_frame.findFirstElement('body'),
                match_el=lambda el: '@' in el.attribute('href'))
        return [el.attribute('href').replace('mailto:', '') for el in els]

    def phone_numbers(self):
        number_match = lambda t: list(phonenumbers.PhoneNumberMatcher(t, 'US'))
        els = self.traverse(self.ghost.main_frame.findFirstElement('body'),
                match_text=number_match)
        return [el.toPlainText() for el in els]

if __name__ == '__main__':
    url = sys.argv[1]
    c = ContactPlugin(url=url)
    print c.process()
