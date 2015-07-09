
#############################################################
#                                                           #
# scrape - a web scraping tool                              #
# written by Hunter Hammond (huntrar@gmail.com)             #
#                                                           #
#############################################################

import argparse
import sys
from urlparse import urlparse

from utils import *
from . import __version__

import lxml.html as lh
import pdfkit as pk


def get_parser():
    parser = argparse.ArgumentParser(description='a web scraping tool')
    parser.add_argument('urls', type=str, nargs='*',
                        help='urls to scrape')
    parser.add_argument('-f', '--filter', type=str, nargs='*', 
                        help='filter lines by keywords, text only')
    parser.add_argument('-c', '--crawl', type=str, nargs='*',
                        help='enter keywords to crawl links')
    parser.add_argument('-ca', '--crawl-all', help='crawl all links',
                        action='store_true')
    parser.add_argument('-l', '--limit', type=int, help='crawl page limit')
    parser.add_argument('-t', '--text', help='write to text instead of pdf',
                        action='store_true')
    parser.add_argument('-vb', '--verbose', help='show pdfkit messages',
                        action='store_true')
    parser.add_argument('-v', '--version', help='display current version',
                        action='store_true')
    return parser


def crawl(args, url, limit):
    # These are keywords to filter links by
    filter_words = args['crawl']

    uncrawled_links = OrderedSet()
    crawled_links = OrderedSet()

    crawl_ct = 0

    links_to_crawl = get_html(url).xpath('//a/@href')
    crawled_links.add(url)
    crawl_ct += 1
    uncrawled_links.update(links_to_crawl)
    
    try:
        while uncrawled_links and (len(crawled_links) < limit or limit is None):
            url = uncrawled_links.pop(last=False)

            if url not in crawled_links and validate_url(url):
                links_to_crawl = get_html(url).xpath('//a/@href')
                crawled_links.add(url)
                crawl_ct += 1
                print('Crawled {} ({}).'.format(url, crawl_ct))
                uncrawled_links.update(links_to_crawl)
    except KeyboardInterrupt:
        pass

    if filter_words:
        return filter(lambda x: x in filter_words, crawled_links)
    else:
        return list(crawled_links)


def write_pages(args, links, filename):
    if args['text']: 
        filename = filename + '.txt'
        print('Attempting to write {} page(s) to {}.'.format(len(links), filename))

        print_pg_num = len(links) > 1

        for i, link in enumerate(links):
            html = get_html(link)

            if len(html) > 0:
                text = get_text(html, args['filter'])
                if text:
                    with open(filename, 'a') as f:
                        # Print page number if number of pages exceeds 1
                        if print_pg_num:
                            f.write('\n\n')
                            f.write('~~~ Page {} ~~~\n'.format(str(i+1)))

                        for line in text:
                            f.write(line)
            else:
                sys.stderr.write('Failed to parse {}.\n'.format(link))
    else:
        filename = filename + '.pdf'
        print('Attempting to write {} page(s) to {}.'.format(len(links), filename))
        
        options = {'ignore-load-errors': None}
        if not args['verbose']:
            options['quiet'] = None
        try:
            pk.from_url(links, filename, options=options)
        except Exception as e:
            sys.stderr.write('Failed to convert to pdf.\n')
            sys.stderr.write(str(e) + '\n')


def scrape(args):
    url = ''
    for u in args['urls']:
        url = clean_url(u)

        base_url = '{url.netloc}'.format(url=urlparse(url))
        base_name = ''
        for b in base_url.split('.'):
            if len(b) > 3:
                base_name = b
                break

        tail_name = url.strip('/').split('/')[-1]
        if '.' in tail_name:
            filename = base_name
        else:
            filename = base_name + '-' + tail_name

        if args['limit']:
            limit = args['limit']
        else:
            limit = None

        if args['crawl'] or args['crawl_all']:
            links = crawl(args, url, limit)
        else:
            links = [url]
        write_pages(args, links, filename)


def command_line_runner():
    parser = get_parser()
    args = vars(parser.parse_args()) 

    if args['version']:
        print(__version__)
        return

    if not args['urls']:
        parser.print_help()
    else:
        scrape(args)



if __name__ == '__main__':
    command_line_runner()
