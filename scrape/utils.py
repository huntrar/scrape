from collections import MutableSet
import random
import requests
import string
import sys

import lxml.html as lh


USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
                'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5',
                'Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.46 Safari/536.5')



class OrderedSet(MutableSet):


    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable


    def __len__(self):
        return len(self.map)


    def __contains__(self, key):
        return key in self.map


    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]


    def update(self, iterable):
        for it in iterable:
            self.add(it)


    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev


    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]


    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]


    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key


    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))


    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)



def get_html(url):
    try:
        # Get HTML response
        headers={'User-Agent' : random.choice(USER_AGENTS)}
        request = requests.get(url, headers=headers)
        return lh.fromstring(request.text.encode('utf-8'))
    except Exception as e:
        sys.stderr.write('Failed to retrieve {}.\n'.format(url))
        sys.stderr.write(str(e) + '\n')
        return []


def get_text(html, kws):
    text = html.xpath('//*[not(self::script)]/text()')
    new_text = []
    for line in text:
        if kws:
            for kw in kws:
                if kw.strip() in line:
                    if line.strip():
                        new_text.append(filter(lambda x: x in string.printable, line.strip().encode('utf-8')) + '\n')
                    break
        else:
            if line.strip():
                new_text.append(filter(lambda x: x in string.printable, line.strip().encode('utf-8')) + '\n')
    return new_text 


def clean_url(url):
    if 'http://' not in url and 'https://' not in url:
        url = 'https://' + url
    if '.' not in url:
        url = url + '.com'
    return url


def validate_url(url):
    if 'http://' not in url and 'https://' not in url:
        return False
    return True

