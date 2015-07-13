#!/usr/bin/env python

#############################################################
#                                                           #
# scrape - a web scraping tool                              #
# written by Hunter Hammond (huntrar@gmail.com)             #
#                                                           #
#############################################################

import argparse
import sys
from urlparse import urlparse, urljoin

import lxml.html as lh
import pdfkit as pk

import utils
from . import __version__


def get_parser():
    parser = argparse.ArgumentParser(description='a web scraping tool')
    parser.add_argument('urls', type=str, nargs='*',
                        help='urls to scrape')
    parser.add_argument('-c', '--crawl', type=str, nargs='*',
                        help='url keywords to crawl links by')
    parser.add_argument('-ca', '--crawl-all', help='crawl all links',
                        action='store_true')
    parser.add_argument('-f', '--filter', type=str, nargs='*', 
                        help='filter lines of text by keywords')
    parser.add_argument('-l', '--limit', type=int, help='set crawl page limit')
    parser.add_argument('-p', '--pdf', help='write to pdf instead of text',
                        action='store_true')
    parser.add_argument('-s', '--restrict', help='restrict domain to that of the seed url',
                        action='store_true')
    parser.add_argument('-v', '--version', help='display current version',
                        action='store_true')
    parser.add_argument('-vb', '--verbose', help='print pdfkit log messages',
                        action='store_true')
    return parser


def crawl(args, base_url):
    # Url keywords for filtering crawled links
    url_keywords = args['crawl']

    # The limit on number of pages to be crawled
    limit = args['limit']

    # Whether links must share the same domain as the seed url
    restrict = args['restrict']

    # Domain of the seed url
    domain = args['domain']

    uncrawled_links = utils.OrderedSet()
    crawled_links = utils.OrderedSet()
    raw_links = utils.OrderedSet()

    html = utils.get_html(base_url)
    if len(html) > 0:
        raw_links.update(html.xpath('//a/@href'))

    ''' Clean, filter, and update links
        clean_url removes url fragments and constructs an absolute url using urlparse's urljoin.
        Also strips punctuation from right end. Pass url and then base url. 
    '''
    if raw_links:
        links = [utils.clean_url(u, base_url) for u in raw_links]
        raw_links.clear()

        ''' Domain may be restricted to the seed domain '''
        if restrict:
            links = filter(lambda x: domain in x, links)

        ''' Links may have keywords to follow them by '''
        if url_keywords:
            for kw in url_keywords:
                links = filter(lambda x: kw in x, links)

        ''' Compare schemeless urls to prevent http:// and https:// duplicates '''
        schemeless_crawled_links = map(utils.remove_scheme, crawled_links)
        uncrawled_links.update(filter(lambda x: utils.remove_scheme(x) not in schemeless_crawled_links, links))

    crawled_links.add(base_url)
    print('Crawled {} (#{}).'.format(base_url, len(crawled_links)))
    
    ''' Follow links found in base url '''
    try:
        while uncrawled_links and (not limit or len(crawled_links) < limit):
            url = uncrawled_links.pop(last=False)

            if utils.validate_url(url):
                html = utils.get_html(url)
                if len(html) > 0:
                    raw_links.update(html.xpath('//a/@href'))

                ''' Clean, filter, and update links
                    clean_url removes url fragments and constructs an absolute url using urlparse's urljoin.
                    Also strips punctuation from right end. Pass url and then base url. 
                '''
                if raw_links:
                    links = [utils.clean_url(u, base_url) for u in raw_links]
                    raw_links.clear()

                    ''' Domain may be restricted to the seed domain '''
                    if restrict:
                        links = filter(lambda x: domain in x, links)

                    ''' Links may have keywords to follow them by '''
                    if url_keywords:
                        for kw in url_keywords:
                            links = filter(lambda x: kw in x, links)

                    ''' Compare schemeless urls to prevent http:// and https:// duplicates '''
                    schemeless_crawled_links = map(utils.remove_scheme, crawled_links)
                    uncrawled_links.update(filter(lambda x: utils.remove_scheme(x) not in schemeless_crawled_links, links))

                if url not in crawled_links:
                    if restrict:
                        if domain in url:
                            crawled_links.add(url)
                            print('Crawled {} (#{}).'.format(url, len(crawled_links)))
                    else: 
                        crawled_links.add(url)
                        print('Crawled {} (#{}).'.format(url, len(crawled_links)))
    except KeyboardInterrupt:
        pass

    # Optional filter keywords passed to --crawl option
    filter_words = args['crawl']
    if filter_words:
        return utils.filter_re(crawled_links, filter_words)

    return list(crawled_links)


def write_links(args, links, file_name):
    if args['pdf']: 
        file_name = file_name + '.pdf'
        utils.clear_file(file_name)

        print('Attempting to write {} page(s) to {}.'.format(len(links), file_name))
        
        ''' Set pdfkit options
            Only ignore errors if there is more than one link
            This is to prevent an empty pdf being written
            But if links > 1 we don't want one failure to prevent writing others
        '''
        options = {}
        
        if len(links) > 1:
            options['ignore-load-errors'] = None

        verbose = args['verbose']
        if not verbose:
            options['quiet'] = None

        try:
            pk.from_url(links, file_name, options=options)
        except Exception as e:
            if verbose:
                print(str(e))
    else:
        file_name = file_name + '.txt'
        utils.clear_file(file_name)

        print('Attempting to write {} page(s) to {}.'.format(len(links), file_name))

        for link in links:
            html = utils.get_html(link)
            if len(html) > 0:
                text = utils.get_text(html, args['filter'])
                if text:
                    utils.write_file(text, file_name)
            else:
                sys.stderr.write('Failed to parse {}.\n'.format(link))


def scrape(args):
    for u in args['urls']:
        url = utils.resolve_url(u)

        ''' Split the url into the following components using urlparse
        scheme, netloc, path, params, query, fragment
        '''
        parsed_url = urlparse(url)

        ''' Construct the output file name from partial domain and end of path
            The proper extension will be added in write_links
        '''
        domain = '{url.netloc}'.format(url=parsed_url)
        if '.' in domain:
            base_url = domain.split('.')[-2]
        else:
            base_url = domain

        args['domain'] = base_url # Only want base domain

        path = '{url.path}'.format(url=parsed_url)
        if '.' in path:
            tail_url = path.split('.')[-2]
        else:
            tail_url = path

        if tail_url:
            if '/' in tail_url:
                tail_url = tail_url.split('/')[-1]
            out_file = base_url + '-' + tail_url
        else:
            out_file = base_url

        ''' Crawl if necessary '''
        if args['crawl'] or args['crawl_all']:
            links = crawl(args, url)
        else:
            links = [url]

        ''' Write links to text or pdf '''
        write_links(args, links, out_file)


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
