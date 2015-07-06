#!/usr/bin/env python
# convert a webpage to text based on keywords

import argparse
import string
import sys
import random
import requests

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

        
def parse_html(html, kws):
    text = html.xpath('//*[not(self::script)]/text()')
    for i, t in enumerate(text):
        for k in kws:
            if k in t:
                yield filter(lambda x: x in string.printable, t.strip().encode('utf-8')) + '\n'
                break


def print_usage():
    sys.stderr.write('usage: scrape.py [url] [keywords..]\n')
    sys.exit()


def run():
    if len(sys.argv) > 2:
        url = sys.argv[1]
        if 'http://' not in url and 'https://' not in url:
            url = 'https://' + url
        keywords = sys.argv[2:]
    else:
        print_usage()

    print('Parsing %s' % url)
    html = get_html(url)
    if html is not None:
        parsed = parse_html(html, keywords)
        filename = url.strip('/').split('/')[-1] + '.txt'
        with open(filename, 'w') as f:
            for line in parsed:
                f.write(line)
        print('Wrote to file %s' % filename)
    else:
        sys.stderr.write('Failed to parse HTML.\n')


if __name__ == '__main__':
    run()
