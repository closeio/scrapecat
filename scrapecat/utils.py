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
        return ret # Don't traverse children if parent node matches.
    if node_info:
        node = parent_node.firstChild()
        for node_type, node_value in node_info:
            node_value = unicode(node_value)
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


def get_children_by_tag_name(el, tag_name):
    el = el.firstChild()
    tag_name = tag_name.lower()
    ret = []
    while not el.isNull():
        if el.tagName().lower() == tag_name:
            ret.append(el)
        el = el.nextSibling()
    return ret


"""
Returns the path how to get to this element.
Sample path: [(u'body', 0), (u'table', 2), (u'tbody', 0), (u'tr', 0), (u'td', 1), (u'a', 0)]
"""
def get_selector_path_for_element(el):
    ps = get_parents(el)
    return [(child.tagName().lower(), [el == child for el in get_children_by_tag_name(parent, child.tagName())].index(True)) for parent, child in zip(ps, ps[1:])]


"""
Returns a unique CSS selector for this element using its path, e.g.
body:nth(0)>table:nth(2)>tbody:nth(0)>tr:nth(0)>td:nth(1)>a:nth(0)
"""
def get_unique_css_selector_for_element(el):
    return '>'.join(['%s:nth(%d)' % (name, pos) for name, pos in get_selector_path_for_element(el)])


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
Takes a list of elements and returns selector paths matching similar elements:  If two or more elements
match a selector tag1:nth(i1)>tag2:nth(i2)>...>tagm:nth(j)...>tagn-2:nth(in-1)>tagn-1:nth(in), where
"tag1" to "tagn" and "i1" to "in" are the same, it will return a path matching elements for any j that exists.
The returned path will have the "nth(j)" value set None to denote that it can be arbitrary. It will include the
elements that matched that path.

Example: If we pass three elements matching body>td:nth(0)>a:nth(2), body>td:nth(3)>a:nth(2) and body>td:nth(4)>a:nth(2),
we will get [([('body', 0), ('td', None), ('a', 2)], els)] as a result.
"""
def find_similar_selector_paths(els):
    if not els:
        return []
    by_length = {}
    for el in els:
        path = get_selector_path_for_element(el)
        path_length = len(path)
        if not path_length in by_length:
            by_length[path_length] = []
        by_length[path_length].append((el, path))

    similar_paths = []

    for length, data in by_length.iteritems():
        while data:
            similar_path_found = False
            el1, p1 = data.pop()

            found_data = []
            found_els = []

            for el2, p2 in data:
                diff = [a!=b for a, b in zip(p1, p2)]
                if diff.count(True) == 1: # one selector is changed
                    idx = diff.index(True)
                    if p1[idx][0] == p2[idx][0]: # same element name
                        if not similar_path_found:
                            similar_path_found = True
                            # Append the path. Note that the found elements list is still being populated.
                            similar_paths.append(([(name, None) if i == idx else (name, n) for i, (name, n) in enumerate(p1)], found_els))
                        # queue removal of (el2, p2) from array
                        found_data.append((el2, p2))
                        found_els.append(el2)

            for found_entry in found_data:
                data.remove(found_entry)
    
    return similar_paths



"""
Resolves a path obtained by get_selector_path_for_element() relative to the passed in element and returns the matching element.
The passed in element is usually be the document. If a path contains None as a position, it returns all matching elements, e.g.
[('body', 0), ('a', None)] would return all "a" elements directly within the body.
"""
def get_elements_for_path(el, path):
    if not path:
        return [el] # Found it
    path = path[:]
    path_el, n = path.pop(0)
    el = el.firstChild()
    ret = []
    while not el.isNull():
        if el.tagName().lower() == path_el.lower():
            if n == None or n == 0:
                ret += get_elements_for_path(el, path)
            if n == 0:
                return ret
            if n != None:
                n -= 1
        el = el.nextSibling()
    return ret




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


""" Traverses the passed in element and returns a tuple of (element, [match1, match2, ...]) where a text match occurs. """
def traverse_extract(el, match_text):
    return [(el, match_text(unicode(el.toPlainText()))) for el in traverse(el, match_text=match_text)]




from phonenumbers.phonenumberutil import format_number, parse, PhoneNumberFormat

def format_us_phone_number(value):
    phone = parse(value, 'US')
    formatted = format_number(phone, PhoneNumberFormat.E164)
    if phone.extension:
        formatted += 'x%s' % phone.extension
    return formatted

# Take the ten characters in front of the number
# and see if they indicate it's a phone or a fax
def number_type(t, number):
    segment = t[t.find(number)-10: t.find(number)]
    if re.search('fax', segment, re.IGNORECASE): return 'fax'
    else: return 'phone'
