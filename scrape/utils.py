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

def get_html(url):
    try:
        # Get HTML response
        headers={'User-Agent' : random.choice(USER_AGENTS)}
        request = requests.get(url, headers=headers)
        return lh.fromstring(request.text.encode('utf-8'))
    except Exception as e:
        sys.stderr.write('Failed to retrieve %s.\n' % url)
        sys.stderr.write(str(e) + '\n')
        return None

def get_text(html, kws):
    text = html.xpath('//*[not(self::script)]/text()')
    for line in text:
        if kws:
            for kw in kws:
                if kw.strip() in line:
                    if line.strip():
                        yield filter(lambda x: x in string.printable, line.strip().encode('utf-8')) + '\n'
                    break
        else:
            if line.strip():
                yield filter(lambda x: x in string.printable, line.strip().encode('utf-8')) + '\n'
            
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

