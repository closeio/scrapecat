import re
from scrapecat.validators import email_re

def traverse(parent_node, match_el=None, match_text=None, depth=0, ignore_tags=None):
    ret = []
    node_info = parent_node.evaluateJavaScript(
            '''(function(el) {
                var ret = []; el = el.firstChild;
                while (el) {
                    ret.push([el.nodeType, el.nodeValue]);
                    el = el.nextSibling;
                } return ret;
            })(this);''')

    if ignore_tags is None:
        ignore_tags = ['SCRIPT', 'NOSCRIPT']

    if match_el and match_el(parent_node):
        ret.append(parent_node)
    if node_info:
        node = parent_node.firstChild()
        for node_type, node_value in node_info:
            if node_type == 1: # element node
                if node.tagName() not in ignore_tags:

                    ret += traverse(node,
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


""" Returns a list of parents of the given element, starting from the root element to the element itself. """
def get_parents(el):
    stack = []
    while not el.isNull():
        stack.insert(0, el)
        el = el.parent()
    return stack


""" Returns a list of common parent elements, from the root element to the nearest parent. """
def common_parents(el1, el2):
    stack1 = get_parents(el1)
    stack2 = get_parents(el2)
    return [a for a, b in zip(stack1, stack2) if a == b]


def nearest_common_parent(el1, el2):
    return common_parents(el1, el2)[-1]


def group_by_common_parents(els1, els2):
    groups = []

    class HashableWebElement(object):
        def __init__(self, element):
            self.element = element

    els1 = [HashableWebElement(el) for el in els1]
    els2 = [HashableWebElement(el) for el in els2]

    """
    Create a sample matrix and match elements if there is a distinct maximum in a row.

    Sample matrix:
    [[8, 8, 12, 8, 8, 8, 8, 8, 8, 8],
     [8, 8, 8, 12, 8, 8, 8, 8, 8, 8],
     [8, 8, 8, 8, 12, 8, 8, 8, 8, 8],
     [8, 8, 8, 8, 8, 12, 8, 8, 8, 8],
     [8, 8, 8, 8, 8, 8, 12, 8, 8, 8],
     [8, 8, 8, 8, 8, 8, 8, 12, 8, 8]]
    """
    parents = {}
    for el in els1:
        parents[el] = get_parents(el.element)
    for el in els2:
        parents[el] = get_parents(el.element)

    def cached_common_parents(el1, el2):
        return [a for a, b in zip(parents[el1], parents[el2]) if a == b]

    matrix = [[len(cached_common_parents(els1[n], els2[m])) for m in range(len(els2))] for n in range(len(els1))]

    for n, row in enumerate(matrix):
        the_max = max(row)
        if row.count(the_max) == 1:
            group_parent = parents[els1[n]][max([i for i in row if i != the_max])]
            groups.append([els1[n].element, els2[row.index(the_max)].element, group_parent])

    return groups


"""
Returns an array of emails found in a string.
"""
def find_emails(s):
    emails = []
    # Split the string at some special characters, so emails like "me@example.com"  or <me@example.com> are found.
    for part in re.split('[ \'"<>:]+', s):
        if email_re.match(part):
            emails.append(part)
    return emails
