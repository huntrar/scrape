from collections import MutableSet
import hashlib
import os
import random
import re
import requests
import string
import sys
from urlparse import urlparse, urljoin

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


    def clear(self):
        while self:
            self.pop()


    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))


    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)



def get_str_html(url):
    try:
        ''' Get text response '''
        headers={'User-Agent' : random.choice(USER_AGENTS)}
        request = requests.get(url, headers=headers)
        return request.text.encode('utf-8')
    except Exception as e:
        sys.stderr.write('Failed to retrieve {}.\n'.format(url))
        sys.stderr.write(str(e) + '\n')
        return ''
    

def hash_text(text):
    m = hashlib.md5()
    m.update(text)
    return m.hexdigest()


def cache_page(page_cache, page_hash):
    page_cache.append(page_hash)
    if len(page_cache) > 10:
        page_cache.pop(0)


def filter_re(lines, regexps):
    if regexps:
        regexps = map(re.compile, regexps)
        matched_lines = []
        for line in lines:
            for regexp in regexps:
                found = regexp.search(line)
                if found:
                    group = found.group()
                    if group:
                        matched_lines.append(line)
        return matched_lines
    return lines


def get_text(html, kws):
    text = filter_re(html.xpath('//*[not(self::script) and not(self::style)]/text()'), kws)
    return [filter(lambda x: x in string.printable, line.strip()) + '\n' for line in text]


def get_domain(url):
    domain = '{url.netloc}'.format(url=urlparse(url))
    if '.' in domain:
        return domain.split('.')[-2]
    return domain


def get_out_file(url, domain=None):
    if domain is None:
        domain = get_domain(url)

    path = '{url.path}'.format(url=urlparse(url))
    if '.' in path:
        tail_url = path.split('.')[-2]
    else:
        tail_url = path

    if tail_url:
        if '/' in tail_url:
            tail_url = tail_url.split('/')[-1]
        return domain + '-' + tail_url
    else:
        return domain


def remove_scheme(url):
    return url.replace('http://', '').replace('https://', '')


def clean_url(url, base_url):
    parsed_url = urlparse(url)
    fragment = '{url.fragment}'.format(url=parsed_url)
    if fragment:
        url = url.split(fragment)[0]
    
    # If no domain was found in url then add the base
    if not '{url.netloc}'.format(url=parsed_url):
        url = urljoin(base_url, url) 
    return url.rstrip(string.punctuation)


def resolve_url(url):
    if '.' not in url:
        url = url + '.com'
    return url.rstrip('/')


def validate_url(url):
    if url and ('http://' in url or 'https://' in url):
        return True
    return False


def clear_file(file_name):
    try:
        os.remove(file_name)
    except OSError:
        pass


def write_file(text, file_name):
    with open(file_name, 'a') as f:
        for line in text:
            if line.strip():
                f.write(line)
        f.write('\n')


def change_directory(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        os.chdir(dir_name)
    else:
        os.chdir(dir_name)


def get_num_parts():
    num_parts = 0
    for file in os.listdir(os.getcwd()):
        if 'PART' in file and file.endswith('.html'):
            num_parts += 1
    return num_parts


def write_part_file(html, part_num=None):
    if part_num is None:
        part_num = get_num_parts() + 1

    f_name = 'PART{}.html'.format(part_num)
    with open(f_name, 'w') as f:
        f.write(html)


def get_part_files(num_parts=None):
    if num_parts is None:
        num_parts = get_num_parts()

    return ['PART{}.html'.format(i) for i in xrange(1, num_parts+1)]


def read_part_files(num_parts=None):
    if num_parts is None:
        num_parts = get_num_parts()

    files = get_part_files(num_parts)
    for file in files:
        with open(file, 'r') as f:
            yield f.read()


def clear_part_files(num_parts=None):
    files = get_part_files(num_parts)
    for file in files:
        clear_file(file)


