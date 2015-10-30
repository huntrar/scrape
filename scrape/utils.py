import hashlib
import os
import random
import re
import string
import sys

import lxml.html as lh
import requests


SYS_VERSION = sys.version_info[0]
if SYS_VERSION == 2:
    try:
        range = xrange
    except NameError:
        pass

try:
    from urllib import getproxies
except ImportError:
    from urllib.request import getproxies

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin


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


def get_proxies():
    ''' Get available proxies to use with requests library '''
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
    ''' Get HTML response as an lxml.html.HtmlElement object '''
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        request = requests.get(url, headers=headers, proxies=get_proxies())
        return lh.fromstring(request.text.encode('utf-8'))
    except Exception as err:
        sys.stderr.write('Failed to retrieve {0}.\n'.format(url))
        sys.stderr.write('{0}\n'.format(str(err)))
        return None


def get_raw_html(url):
    ''' Get HTML response as a str object '''
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        request = requests.get(url, headers=headers, proxies=get_proxies())
        return request.text.encode('utf-8')
    except Exception as err:
        sys.stderr.write('Failed to retrieve {0} as str.\n'.format(url))
        sys.stderr.write('{0}\n'.format(str(err)))
        return None


def hash_text(text):
    ''' Return MD5 hash '''
    md5 = hashlib.md5()
    md5.update(text)
    return md5.hexdigest()


def cache_link(link_cache, link_hash, cache_size):
    ''' Add a link to cache '''
    link_cache.append(link_hash)
    if len(link_cache) > cache_size:
        link_cache.pop(0)


def filter_re(lines, regexps):
    ''' Filter text using regular expressions '''
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
    ''' Append @ to attributes and resolve text -> text() for XPath '''
    if attr:
        if 'text' in attr:
            return 'text()'
        else:
            attr = attr.lstrip('@')

    if attr:
        return '@' + attr
    return None


def filter_text(html, filter_words=None, attributes=None, filter_html=True):
    ''' Filter text using keywords and attributes '''
    if attributes:
        attributes = [clean_attr(x) for x in attributes]
        attributes = [x for x in attributes if x]
    else:
        attributes = ['text()']

    text = []
    for attr in attributes:
        if filter_html:
            new_text = html.xpath('//*[not(self::script) and \
                                  not(self::style)]/{0}'.format(attr))
        else:
            new_text = html.split('\n')

        if filter_words:
            new_text = filter_re(new_text, filter_words)

        text += new_text

    return [''.join(x for x in line.strip() if x in string.printable) + '\n'
            for line in text]


def get_domain(url):
    ''' Get the domain of a URL '''
    domain = '{url.netloc}'.format(url=urlparse(url))
    if '.' in domain:
        return domain.split('.')[-2]
    return domain


def get_out_filename(url, domain=None):
    ''' Construct the output file name from partial domain and end of path '''
    if domain is None:
        domain = get_domain(url)

    path = '{url.path}'.format(url=urlparse(url))
    if '.' in path:
        tail_url = path.split('.')[-2]
    else:
        tail_url = path

    if tail_url:
        if '/' in tail_url:
            tail_url = [x for x in tail_url.split('/') if x][-1]
        return domain + '-' + tail_url
    else:
        return domain


def add_scheme(url):
    ''' Add scheme to URL '''
    return 'http://{0}'.format(url)


def remove_scheme(url):
    ''' Remove scheme from URL '''
    return url.replace('http://', '').replace('https://', '')


def check_scheme(url):
    ''' Check URL for a scheme '''
    if url and (url.startswith('http://') or url.startswith('https://')):
        return True
    return False


def clean_url(url, base_url):
    ''' Remove URL fragments and add base URL if necessary '''
    parsed_url = urlparse(url)

    ''' Remove URL fragments '''
    fragment = '{url.fragment}'.format(url=parsed_url)
    if fragment:
        url = url.split(fragment)[0]

    ''' If no domain was found in URL then add the base URL to it '''
    if not '{url.netloc}'.format(url=parsed_url):
        url = urljoin(base_url, url)
    return url.rstrip(string.punctuation)


def add_url_ext(url):
    ''' Add .com to url '''
    url = url.rstrip('/')
    if '.' not in url:
        url = '{0}.com'.format(url)
    return url


def remove_file(file_name):
    ''' Remove a file from disk '''
    try:
        os.remove(file_name)
        return True
    except (OSError, IOError):
        return False


def write_file(text, file_name):
    ''' Write a file to disk '''
    try:
        with open(file_name, 'a') as f:
            for line in text:
                if line.strip():
                    f.write(line)
            f.write('\n')
        return True
    except (OSError, IOError):
        sys.stderr.write('Failed to write {0}.\n'.format(file_name))
        return False


def mkdir_and_cd(dir_name):
    ''' Change directory and/or create it if necessary '''
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        os.chdir(dir_name)
    else:
        os.chdir(dir_name)


def get_num_part_files():
    ''' Get the number of PART.html files currently saved to disk '''
    num_parts = 0
    for f_name in os.listdir(os.getcwd()):
        if 'PART' in f_name and f_name.endswith('.html'):
            num_parts += 1
    return num_parts


def write_part_file(html, part_num=None):
    ''' Write PART.html files to disk '''
    if part_num is None:
        part_num = get_num_part_files() + 1

    ''' Decode bytes to str if necessary for Python 3 '''
    if type(html) == bytes:
        html = html.decode('utf-8')

    f_name = 'PART{0}.html'.format(part_num)
    with open(f_name, 'w') as f:
        f.write(html)


def get_part_filenames(num_parts=None):
    ''' Get numbered PART.html filenames '''
    if num_parts is None:
        num_parts = get_num_part_files()

    return ['PART{0}.html'.format(i) for i in xrange(1, num_parts+1)]


def read_files(files):
    ''' Read files from disk using generator construct '''
    if isinstance(files, list):
        for f_name in files:
            with open(f_name, 'r') as f:
                yield f.read()
    else:
        with open(files, 'r') as f:
            yield f.read()


def remove_part_files(num_parts=None):
    ''' Remove PART.html files from disk '''
    files = get_part_filenames(num_parts)
    for f_name in files:
        remove_file(f_name)
