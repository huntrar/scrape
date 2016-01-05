"""Contains scrape utility functions"""

from cgi import escape
import hashlib
import os
import random
import re
import shutil
import string
import sys
import time

import lxml.html as lh
import requests


SYS_VERSION = sys.version_info[0]
if SYS_VERSION == 2:
    from urllib import getproxies
    from urlparse import urlparse, urljoin

    range = xrange
else:
    from urllib.request import getproxies
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
    """Get available proxies to use with requests library"""
    proxies = getproxies()
    filtered_proxies = {}
    for key, value in proxies.items():
        if key.startswith('http://'):
            if not value.startswith('http://'):
                filtered_proxies[key] = 'http://{0}'.format(value)
            else:
                filtered_proxies[key] = value
    return filtered_proxies


def get_resp(url):
    """Get webpage response as an lxml.html.HtmlElement object"""
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        request = requests.get(url, headers=headers, proxies=get_proxies())
        return lh.fromstring(request.text.encode('utf-8'))
    except Exception:
        sys.stderr.write('Failed to retrieve {0}.\n'.format(url))
        raise


def get_raw_resp(url):
    """Get webpage response as a str object"""
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        request = requests.get(url, headers=headers, proxies=get_proxies())
        return request.text.encode('utf-8')
    except Exception:
        sys.stderr.write('Failed to retrieve {0} as str.\n'.format(url))
        raise


def hash_text(text):
    """Return MD5 hash"""
    md5 = hashlib.md5()
    md5.update(text)
    return md5.hexdigest()


def cache_link(link_cache, link_hash, cache_size):
    """Add a link to cache"""
    link_cache.append(link_hash)
    if len(link_cache) > cache_size:
        link_cache.pop(0)


def re_filter(text, regexps):
    """Filter text using regular expressions"""
    if regexps:
        regexps = [re.compile(x) for x in regexps]
        matched_text = []
        for line in text:
            for regexp in regexps:
                if line not in matched_text:
                    found = regexp.search(line)
                    if found:
                        group = found.group()
                        if group:
                            matched_text.append(line)
        if matched_text:
            # Last line is an unnecessary newline
            return matched_text[:-1]
    return text


def clean_attr(attr):
    """Append @ to attributes and resolve text -> text() for XPath"""
    if attr:
        if 'text' in attr:
            return 'text()'
        else:
            attr = attr.lstrip('@')
    if attr:
        return '@' + attr
    return None


def parse_html(infile, xpath):
    """Filter HTML using XPath"""
    if not isinstance(infile, lh.HtmlElement):
        infile = lh.fromstring(infile)
    infile = infile.xpath(xpath)
    if not infile:
        raise ValueError('XPath {0} returned no results.'.format(xpath))
    return infile


def remove_whitespace(text):
    """Remove unnecessary whitespace while keeping logical structure

       Keyword arguments:
       text -- text to remove whitespace from (list)

       The goal is to remove unnecessary whitespace while retaining logical
       structure such as paragraph separation.
       We also want to remove unnecessary whitespace between words on a line.
       Removes whitespace at the start and end of the text.
    """
    clean_text = []
    curr_line = ''
    # Remove any newlines that follow two lines of whitespace consecutively
    # Also remove whitespace at start and end of text
    while text:
        if not curr_line:
            # Find the first line that is not whitespace and add it
            curr_line = text.pop(0)
            while not curr_line.strip() and text:
                curr_line = text.pop(0)
            if curr_line.strip():
                clean_text.append(curr_line)
        else:
            # Filter the rest of the lines
            curr_line = text.pop(0)
            if text:
                if curr_line.strip():
                    clean_text.append(curr_line)
                else:
                    # If the current line is whitespace then make sure there is
                    # no more than one consecutive line of whitespace following
                    if not text[0].strip():
                        if len(text) > 1 and text[1].strip():
                            clean_text.append(curr_line)
                    else:
                        clean_text.append(curr_line)
            else:
                # Add the final line if it is not whitespace
                if curr_line.strip():
                    clean_text.append(curr_line)

    # Now filter each individual line for extraneous whitespace
    cleaner_text = []
    clean_line = ''
    for line in clean_text:
        clean_line = ' '.join(line.split())
        if not clean_line.strip():
            clean_line += '\n'
        cleaner_text.append(clean_line)
    return cleaner_text


def parse_text(infile, xpath=None, filter_words=None, attributes=None):
    """Filter text using XPath, regex keywords, and tag attributes

       Keyword arguments:
       infile -- HTML or text content to parse (list)
       xpath -- an XPath expression (str)
       filter_words -- regex keywords (list)
       attributes -- HTML tag attributes (list)

       Return a list of strings of text.
    """
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
        text_xpath = '//*[not(self::script) and not(self::style)]'
        for attr in attributes:
            for infile in infiles:
                if isinstance(infile, lh.HtmlElement):
                    new_text = infile.xpath('{0}/{1}'.format(text_xpath, attr))
                else:
                    # re.split preserves delimeters place in the list
                    new_text = [x for x in re.split('(\n)', infile) if x]
                text += new_text

    if filter_words is not None:
        text = re_filter(text, filter_words)
    return [''.join(x for x in line if x in string.printable)
            for line in remove_whitespace(text) if line]


def get_domain(url):
    """Get the domain of a URL"""
    domain = '{url.netloc}'.format(url=urlparse(url))
    if '.' in domain:
        return domain.split('.')[-2]
    return domain


def get_outfilename(url, domain=None):
    """Construct the output filename from partial domain and end of path"""
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

        # Keep length of return string below or equal to max_len
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
                    # Add as many tail pieces that can fit
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
        return '{0}-{1}'.format(domain, tail_url).lower()
    else:
        return domain.lower()


def add_scheme(url):
    """Add scheme to URL"""
    return 'http://{0}'.format(url)


def remove_scheme(url):
    """Remove scheme from URL"""
    return url.replace('http://', '').replace('https://', '')


def check_scheme(url):
    """Check URL for a scheme"""
    if url and (url.startswith('http://') or url.startswith('https://')):
        return True
    return False


def clean_url(url, base_url):
    """Remove URL fragments and add base URL if necessary"""
    parsed_url = urlparse(url)
    fragment = '{url.fragment}'.format(url=parsed_url)
    if fragment:
        url = url.split(fragment)[0]
    if not '{url.netloc}'.format(url=parsed_url):
        url = urljoin(base_url, url)
    return url.rstrip(string.punctuation)


def has_ext(url):
    """Return whether the url has an extension (unreliable in some cases)"""
    if 'www.' in url:
        url = url.replace('www.', '')
    parsed_url = urlparse(url)
    if parsed_url.path and not parsed_url.netloc:
        return bool(os.path.splitext(parsed_url.path)[1])
    elif parsed_url.netloc:
        return bool(os.path.splitext(parsed_url.netloc)[1])
    return False


def add_url_ext(url):
    """Add .com extension to url if none found"""
    url = url.rstrip('/')
    if not has_ext(url):
        url = '{0}.com'.format(url)
    return url


def remove_file(filename):
    """Remove a file from disk"""
    try:
        os.remove(filename)
        return True
    except (OSError, IOError):
        return False


def write_file(text, filename):
    """Write a file to disk"""
    try:
        if not text:
            return False
        with open(filename, 'a') as outfile:
            for line in text:
                if line:
                    outfile.write(line)
        return True
    except (OSError, IOError):
        sys.stderr.write('Failed to write {0}.\n'.format(filename))
        return False


def mkdir_and_cd(dirname):
    """Change directory and/or create it if necessary"""
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        os.chdir(dirname)
    else:
        os.chdir(dirname)


def get_num_part_files():
    """Get the number of PART.html files currently saved to disk"""
    num_parts = 0
    for filename in os.listdir(os.getcwd()):
        if filename.startswith('PART') and filename.endswith('.html'):
            num_parts += 1
    return num_parts


def write_part_images(url, raw_html, html, filename):
    """Write image files associated with HTML to disk and substitute filenames

       Keywords arguments:
       url -- the URL from which the HTML has been extracted from (str)
       raw_html -- unparsed HTML file content (list)
       html -- parsed HTML file content (lxml.html.HtmlElement) (default: None)
       filename -- the PART.html filename (str)

       Return raw HTML with image names replaced with local image filenames.
    """
    save_dirname = '{0}_files'.format(os.path.splitext(filename)[0])
    if not os.path.exists(save_dirname):
        os.makedirs(save_dirname)
    images = html.xpath('//img/@src')
    internal_image_urls = [x for x in images if x.startswith('/')]

    headers = {'User-Agent': random.choice(USER_AGENTS)}
    for img_url in images:
        img_name = img_url.split('/')[-1]
        if "?" in img_name:
            img_name = img_name.split('?')[0]
        if not os.path.splitext(img_name)[1]:
            img_name = '{0}.jpeg'.format(img_name)

        try:
            full_img_name = os.path.join(save_dirname, img_name)
            with open(full_img_name, 'wb') as img:
                if img_url in internal_image_urls:
                    # Internal images need base url added
                    full_img_url = '{0}{1}'.format(url.rstrip('/'), img_url)
                else:
                    # External image
                    full_img_url = img_url
                img_content = requests.get(full_img_url, headers=headers,
                                           proxies=get_proxies()).content
                img.write(img_content)
                raw_html = raw_html.replace(escape(img_url), full_img_name)
        except (OSError, IOError):
            pass
        time.sleep(random.uniform(0, 0.5))  # Slight delay between downloads
    return raw_html


def write_part_file(args, url, raw_html, html=None, part_num=None):
    """Write PART.html files to disk and save images to a PART_files directory

       Keyword arguments:
       args -- program arguments (dict)
       raw_html -- unparsed HTML file content (list)
       html -- parsed HTML file content (lxml.html.HtmlElement) (default: None)
       part_num -- PART(#).html file number (int) (default: None)
    """
    if part_num is None:
        part_num = get_num_part_files() + 1
    filename = 'PART{0}.html'.format(part_num)

    # Decode bytes to str if necessary for Python 3
    if type(raw_html) == bytes:
        raw_html = raw_html.decode('ascii', 'ignore')
    # Convert html to an lh.HtmlElement object for parsing/saving images
    if html is None:
        html = lh.fromstring(raw_html)

    # Parse HTML if XPath entered
    if args['xpath']:
        raw_html = parse_html(html, args['xpath'])
        if isinstance(raw_html, list):
            if not isinstance(raw_html[0], lh.HtmlElement):
                raise ValueError('XPath should return an HtmlElement object.')
        else:
            if not isinstance(raw_html, lh.HtmlElement):
                raise ValueError('XPath should return an HtmlElement object.')

    # Write HTML and possibly images to disk
    if raw_html:
        if not args['no_images'] and (args['pdf'] or args['html']):
            raw_html = write_part_images(url, raw_html, html, filename)
        with open(filename, 'w') as part:
            if not isinstance(raw_html, list):
                raw_html = [raw_html]
                if isinstance(raw_html[0], lh.HtmlElement):
                    for elem in raw_html:
                        part.write(lh.tostring(elem))
                else:
                    for line in raw_html:
                        part.write(line)


def get_part_filenames(num_parts=None, start_num=0):
    """Get numbered PART.html filenames"""
    if num_parts is None:
        num_parts = get_num_part_files()
    return ['PART{0}.html'.format(i) for i in range(start_num+1, num_parts+1)]


def read_files(filenames):
    """Read a file into memory."""
    if isinstance(filenames, list):
        for filename in filenames:
            with open(filename, 'r') as infile:
                return infile.read()
    else:
        with open(filenames, 'r') as infile:
            return infile.read()


def remove_part_images(filename):
    """Remove PART(#)_files directory containing images from disk"""
    dirname = '{0}_files'.format(os.path.splitext(filename)[0])
    if os.path.exists(dirname):
        shutil.rmtree(dirname)


def remove_part_files(num_parts=None):
    """Remove PART(#).html files and image directories from disk"""
    filenames = get_part_filenames(num_parts)
    for filename in filenames:
        remove_part_images(filename)
        remove_file(filename)
