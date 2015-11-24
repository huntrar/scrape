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


def parse_html(infile, xpath):
    ''' Filter HTML using XPath '''
    if not isinstance(infile, lh.HtmlElement):
        infile = lh.fromstring(infile)

    infile = infile.xpath(xpath)
    if not infile:
        raise ValueError('XPath {0} returned no results.'.format(xpath))
    return infile


def parse_text(infile, xpath=None, filter_words=None, attributes=None):
    ''' Filter text using XPath, regex keywords, and tag attributes '''
    infiles = []
    text = []
    if xpath is not None:
        infile = parse_html(infile, xpath)

        if isinstance(infile, list):
            if isinstance(infile[0], lh.HtmlElement):
                infiles = list(infile)
            else:
                text = [line + '\n' for line in infile]
        elif isinstance(infile, lh.HtmlElement):
            infiles = [infile]
        else:
            text = [infile]
    else:
        infiles = [infile]

    if attributes is not None:
        attributes = [clean_attr(x) for x in attributes]
        attributes = [x for x in attributes if x]
    else:
        attributes = ['text()']

    if not text:
        for attr in attributes:
            for infile in infiles:
                if isinstance(infile, lh.HtmlElement):
                    new_text = infile.xpath('//*[not(self::script) and \
                                          not(self::style)]/{0}'.format(attr))
                else:
                    new_text = [x for x in re.split('(\n)', infile) if x]
                text += new_text

    if filter_words is not None:
        text = filter_re(text, filter_words)

    ''' Remove unnecessary whitespace and carriage returns '''
    clean_text = []
    curr_line = ''
    while text:
        curr_line = text.pop(0)

        if text:
            if not curr_line.strip():
                ''' Current line is whitespace, add if next line is not '''
                if text[0].strip():
                    clean_text.append(curr_line.replace('\r', ''))
            else:
                ''' Current line is not whitespace '''
                clean_text.append(curr_line.replace('\r', ''))
        else:
            ''' Add the final line in text if it is not whitespace '''
            if curr_line.strip():
                clean_text.append(curr_line.replace('\r', ''))
    return [''.join(x for x in line if x in string.printable)
            for line in clean_text if line]


def get_domain(url):
    ''' Get the domain of a URL '''
    domain = '{url.netloc}'.format(url=urlparse(url))
    if '.' in domain:
        return domain.split('.')[-2]
    return domain


def get_outfilename(url, domain=None):
    ''' Construct the output filename from partial domain and end of path '''
    if domain is None:
        domain = get_domain(url)

    path = '{url.path}'.format(url=urlparse(url))
    if '.' in path:
        tail_url = path.split('.')[-2]
    else:
        tail_url = path

    if tail_url:
        if '/' in tail_url:
            tail_pieces = [x for x in tail_url.split('/') if x]
            tail_url = tail_pieces[-1]

        ''' Keep length of return string below or equal to max_len '''
        max_len = 24
        if domain:
            max_len -= (len(domain) + 1)
        if len(tail_url) > max_len:
            if '-' in tail_url:
                tail_pieces = [x for x in tail_url.split('-') if x]
                tail_url = tail_pieces.pop(0)
                if len(tail_url) > max_len:
                    tail_url = tail_url[:max_len]
                else:
                    ''' Add as many tail pieces that can fit '''
                    tail_len = 0
                    for piece in tail_pieces:
                        tail_len += len(piece)
                        if tail_len <= max_len:
                            tail_url += '-' + piece
                        else:
                            break
            else:
                tail_url = tail_url[:max_len]

        if not domain:
            return tail_url
        return (domain + '-' + tail_url).lower()
    else:
        return domain.lower()


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


def remove_file(filename):
    ''' Remove a file from disk '''
    try:
        os.remove(filename)
        return True
    except (OSError, IOError):
        return False


def write_file(text, filename):
    ''' Write a file to disk '''
    try:
        if not text:
            return False
        with open(filename, 'a') as f:
            for line in text:
                if line:
                    f.write(line)
        return True
    except (OSError, IOError):
        sys.stderr.write('Failed to write {0}.\n'.format(filename))
        return False


def mkdir_and_cd(dirname):
    ''' Change directory and/or create it if necessary '''
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        os.chdir(dirname)
    else:
        os.chdir(dirname)


def get_num_part_files():
    ''' Get the number of PART.html files currently saved to disk '''
    num_parts = 0
    for filename in os.listdir(os.getcwd()):
        if filename.startswith('PART') and filename.endswith('.html'):
            num_parts += 1
    return num_parts


def write_part_file(args, html, part_num=None):
    ''' Write PART.html files to disk '''
    if part_num is None:
        part_num = get_num_part_files() + 1

    ''' Decode bytes to str if necessary for Python 3 '''
    if type(html) == bytes:
        html = html.decode('ascii', 'ignore')

    ''' Parse HTML if XPath entered '''
    if args['xpath']:
        html = parse_html(html, args['xpath'])
        if isinstance(html, list):
            if not isinstance(html[0], lh.HtmlElement):
                raise ValueError('XPath should return an HtmlElement object.')
        else:
            if not isinstance(html, lh.HtmlElement):
                raise ValueError('XPath should return an HtmlElement object.')

    filename = 'PART{0}.html'.format(part_num)
    with open(filename, 'w') as f:
        if isinstance(html, list) and html:
            if isinstance(html[0], lh.HtmlElement):
                for elem in html:
                    f.write(lh.tostring(elem))
            else:
                for line in html:
                    f.write(line)
        else:
            if isinstance(html, lh.HtmlElement):
                f.write(lh.tostring(html))
            else:
                f.write(html)


def get_part_filenames(num_parts=None):
    ''' Get numbered PART.html filenames '''
    if num_parts is None:
        num_parts = get_num_part_files()

    return ['PART{0}.html'.format(i) for i in range(1, num_parts + 1)]


def read_files(filenames, chunk_size=1024):
    """Generator function to read a file in chunks.

        Keyword arguments:
        filenames -- name of file to read in
        chunk_size -- size of file chunks in bytes (default 1024)
    """
    data = ''
    if isinstance(filenames, list):
        for filename in filenames:
            with open(filename, 'r') as f:
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    yield data
    else:
        with open(filenames, 'r') as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                yield data


def remove_part_files(num_parts=None):
    ''' Remove PART.html files from disk '''
    filenames = get_part_filenames(num_parts)
    for filename in filenames:
        remove_file(filename)
