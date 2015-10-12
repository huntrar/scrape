import hashlib
import os
import random
import re
import string
import sys
from urlparse import urlparse, urljoin

import lxml.html as lh
import requests


try:
    from urllib import getproxies
except ImportError:
    from urllib.request import getproxies


USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) '
               'Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) '
               'Gecko/20100 101 Firefox/22.0',
               'Mozilla/5.0 (Windows NT 6.1; rv:11.0) '
               'Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) '
               'AppleWebKit/536.5 (KHTML, like Gecko) '
               'Chrome/19.0.1084.46 Safari/536.5',
               'Mozilla/5.0 (Windows; Windows NT 6.1) '
               'AppleWebKit/536.5 (KHTML, like Gecko) '
               'Chrome/19.0.1084.46 Safari/536.5')

CACHE_SIZE = 10 # Number of pages to temporarily cache for preventing dupes


def get_proxies():
    proxies = getproxies()
    filtered_proxies = {}
    for key, value in proxies.items():
        if key.startswith('http://'):
            if not value.startswith('http://'):
                filtered_proxies[key] = 'http://{0}'.format(value)
            else:
                filtered_proxies[key] = value
    return filtered_proxies


def get_html(url):
    try:
        ''' Get HTML response as an lxml.html.HtmlElement object '''
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        request = requests.get(url, headers=headers, proxies=get_proxies())
        return lh.fromstring(request.text.encode('utf-8'))
    except Exception as err:
        sys.stderr.write('Failed to retrieve {0}.\n'.format(url))
        sys.stderr.write('{0}\n'.format(str(err)))
        return None


def get_raw_html(url):
    try:
        ''' Get HTML response as a string object '''
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        request = requests.get(url, headers=headers, proxies=get_proxies())
        return request.text.encode('utf-8')
    except Exception as err:
        sys.stderr.write('Failed to retrieve {0}.\n'.format(url))
        sys.stderr.write('{0}\n'.format(str(err)))
        return None


def hash_text(text):
    md5 = hashlib.md5()
    md5.update(text)
    return md5.hexdigest()


def cache_page(page_cache, page_hash):
    page_cache.append(page_hash)
    if len(page_cache) > CACHE_SIZE:
        page_cache.pop(0)


def filter_re(lines, regexps):
    if regexps:
        regexps = [re.compile(x) for x in regexps]
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


def clean_attr(attr):
    if attr:
        if 'text' in attr:
            return 'text()'
        else:
            attr = attr.lstrip('@')

    if attr:
        return '@' + attr
    return None


def get_text(html, filter_words=None, attributes=None):
    ''' attributes is the tag attribute(s) to extract from the page
        if no attribute was supplied then clean_attr assumes text
    '''
    if attributes:
        attributes = [clean_attr(x) for x in attributes]
        attributes = [x for x in attributes if x]
    else:
        attributes = ['text()']

    text = []
    for attr in attributes:
        new_text = html.xpath('//*[not(self::script) and \
                              not(self::style)]/{0}'.format(attr))

        if filter_words:
            new_text = filter_re(new_text, filter_words)

        text += new_text

    return [filter(lambda x: x in string.printable, line.strip()) + '\n'\
            for line in text]



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

    ''' If no domain was found in url then add the base '''
    if not '{url.netloc}'.format(url=parsed_url):
        url = urljoin(base_url, url)
    return url.rstrip(string.punctuation)


def resolve_url(url):
    if '.' not in url:
        url = url + '.com'
    return url.rstrip('/')


def validate_url(url):
    if url and (url.startswith('http://') or url.startswith('https://')):
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

    f_name = 'PART{0}.html'.format(part_num)
    with open(f_name, 'w') as f:
        f.write(html)


def get_part_files(num_parts=None):
    if num_parts is None:
        num_parts = get_num_parts()

    return ['PART{0}.html'.format(i) for i in xrange(1, num_parts+1)]


def read_files(files):
    if isinstance(files, list):
        for file in files:
            with open(file, 'r') as f:
                yield f.read()
    else:
        with open(file, 'r') as f:
            yield f.read()


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


