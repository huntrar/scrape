#!/usr/bin/env python

#############################################################
#                                                           #
# scrape - a web scraping tool                              #
# written by Hunter Hammond (huntrar@gmail.com)             #
#                                                           #
#############################################################

import argparse
import os
import sys

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
    parser.add_argument('-fl', '--files', help='keep .html files instead of writing to text',
                        action='store_true')
    parser.add_argument('-l', '--limit', type=int, help='set crawl page limit')
    parser.add_argument('-p', '--pdf', help='write to pdf instead of text',
                        action='store_true')
    parser.add_argument('-s', '--strict', help='restrict crawling to domain of seed url',
                        action='store_true')
    parser.add_argument('-v', '--version', help='display current version',
                        action='store_true')
    parser.add_argument('-vb', '--verbose', help='print log and error messages',
                        action='store_true')
    return parser


def crawl(args, base_url):
    # Url keywords for filtering crawled links
    url_keywords = args['crawl']

    # The limit on number of pages to be crawled
    limit = args['limit']

    # Whether links must share the same domain as the seed url
    strict = args['strict']

    # Domain of the seed url
    domain = args['domain']
    
    # Print error messages or not
    verbose = args['verbose']

    ''' crawled_links holds already crawled urls
        uncrawled_links holds urls to pop off from as a stack
    '''
    crawled_links = set()
    uncrawled_links = utils.OrderedSet()

    html = utils.get_str_html(base_url)
    if len(html) > 0:
        ''' Convert html text to HtmlElement object '''
        lh_html = lh.fromstring(html)

        ''' Clean, filter, and update links '''
        new_links = [utils.clean_url(u, base_url) for u in lh_html.xpath('//a/@href')]

        ''' Domain may be restricted to the seed domain '''
        if strict:
            new_links = filter(lambda x: domain in x, new_links)

        ''' Links may have keywords to follow them by '''
        if url_keywords:
            for kw in url_keywords:
                new_links = filter(lambda x: kw in x, new_links)

        ''' Update uncrawled links with new links, add scheme-less url to crawled links
            write_part_file creates a temporary PART.html file to be processed in write_pages '''
        uncrawled_links.update(new_links)
        crawled_links.add(utils.remove_scheme(base_url))
        utils.write_part_file(html, len(crawled_links))
        print('Crawled {} (#{}).'.format(base_url, len(crawled_links)))
        
        ''' Follow links found in base url
            Create a page cache, limit of 10 entries defined in cache_page in utils.py '''
        page_cache = []
        try:
            while uncrawled_links and (not limit or len(crawled_links) < limit):
                ''' Find the next uncrawled link and crawl it '''
                url = uncrawled_links.pop(last=False)

                ''' Compare scheme-less urls to prevent http:// and https:// duplicates '''
                if utils.validate_url(url) and utils.remove_scheme(url) not in crawled_links:
                    ''' Compute a hash of the page and check if it is in the page cache '''
                    html = utils.get_str_html(url)
                    page_hash = utils.hash_text(html)

                    if page_hash not in page_cache:
                        utils.cache_page(page_cache, page_hash)

                        if len(html) > 0:
                            ''' Convert html text to HtmlElement object '''
                            lh_html = lh.fromstring(html)

                            ''' Generate and clean new links '''
                            new_links = [utils.clean_url(u, base_url) for u in lh_html.xpath('//a/@href')]

                            ''' Links may have keywords to follow them by '''
                            if url_keywords:
                                for kw in url_keywords:
                                    new_links = utils.filter_re(new_links, kw)

                            ''' Domain may be restricted to the seed domain '''
                            if strict:
                                if domain in url:
                                    new_links = filter(lambda x: domain in x, new_links)

                                    ''' Update uncrawled links with new links, add scheme-less url to crawled links
                                        write_part_file creates a temporary PART.html file to be processed in write_pages '''
                                    uncrawled_links.update(new_links)
                                    crawled_links.add(utils.remove_scheme(url))
                                    utils.write_part_file(html, len(crawled_links))
                                    print('Crawled {} (#{}).'.format(url, len(crawled_links)))
                                else:
                                    if verbose:
                                        sys.stderr.write('Domain {} was not found in {}.\n'.format(domain, url))
                            else: 
                                ''' Update uncrawled links with new links, add scheme-less url to crawled links
                                    write_part_file creates a temporary PART.html file to be processed in write_pages '''
                                uncrawled_links.update(new_links)
                                crawled_links.add(utils.remove_scheme(url))
                                utils.write_part_file(html, len(crawled_links))
                                print('Crawled {} (#{}).'.format(url, len(crawled_links)))
                        else:
                            if verbose:
                                sys.stderr.write('Failed to parse {}.\n'.format(url))
                    else:
                        if verbose:
                            sys.stderr.write('{} already in cache.\n'.format(url))
                else:
                    if verbose:
                        sys.stderr.write('{} was already crawled, or failed to validate.\n'.format(url))
        except KeyboardInterrupt:
            pass

    return list(crawled_links)


def write_pages(args, pages, file_name):
    if args['pdf']: 
        file_name = file_name + '.pdf'
        utils.clear_file(file_name)

        print('Attempting to write {} page(s) to {}.'.format(len(pages), file_name))
        
        ''' Set pdfkit options
            Only ignore errors if there is more than one page
            This is to prevent an empty pdf being written
            But if pages > 1 we don't want one failure to prevent writing others
        '''
        options = {}
        
        if len(pages) > 1:
            options['ignore-load-errors'] = None

        verbose = args['verbose']
        if not verbose:
            options['quiet'] = None

        ''' Gets PART.html filenames '''
        files = utils.get_part_files(len(pages))

        ''' Attempt conversion to PDF '''
        try:
            pk.from_file(files, file_name, options=options)
        except Exception as e:
            if verbose:
                print(str(e))
    else:
        file_name = file_name + '.txt'
        utils.clear_file(file_name)

        print('Attempting to write {} page(s) to {}.'.format(len(pages), file_name))

        ''' Reads PART.html files '''
        for i, html in enumerate(utils.read_part_files(len(pages))):
            ''' Convert html text to HtmlElement object '''
            html = lh.fromstring(html)

            if len(html) > 0:
                ''' Parse each page's html with lxml.html and get non-script text '''
                text = utils.get_text(html, args['filter'])

                if text:
                    utils.write_file(text, file_name)
            else:
                sys.stderr.write('Failed to parse part file {}.\n'.format(i+1))

    ''' Remove PART.html files '''
    utils.clear_part_files()


def scrape(args):
    base_dir = os.getcwd()
    for u in args['urls']:
        try:
            ''' resolve_url appends .com if no extension found, also rstrips / '''
            url = utils.resolve_url(u)

            ''' Construct the output file name from partial domain and end of path
                The proper extension will be added in write_pages
            '''
            domain = utils.get_domain(url)
            args['domain'] = domain

            if args['files']:
                ''' Keep all scraped .html files and place them in a domain subdirectory
                    change_directory creates the directory if it doesn't exist and calls chdir '''
                utils.change_directory(domain)

            if args['crawl'] or args['crawl_all']:
                ''' crawl traverses and saves all pages as PART.html files '''
                pages = crawl(args, url)
            else:
                pages = [url]
                utils.write_part_file(utils.get_str_html(url), len(pages))

            if args['files']:
                ''' Return to base directory '''
                os.chdir(base_dir)
            else:
                ''' Write pages to text or pdf '''
                out_file = utils.get_out_file(url, domain)
                write_pages(args, pages, out_file)

        except Exception as e:
            if args['files']:
                ''' Return to base directory '''
                os.chdir(base_dir)
            else:
                ''' Remove PART.html files '''
                utils.clear_part_files()

            raise e


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
