#!/usr/bin/env python

######################################################################
#                                                                    #
# scrape - a command-line web scraping tool                          #
# written by Hunter Hammond (huntrar@gmail.com)                      #
#                                                                    #
######################################################################

from __future__ import absolute_import, print_function
import argparse as argp
import os
import sys

import lxml.html as lh
import pdfkit as pk

from scrape.orderedset import OrderedSet
from scrape import utils
from . import __version__


SYS_VERSION = sys.version_info[0]
if SYS_VERSION == 2:
    try:
        input = raw_input
    except NameError:
        pass

LINK_CACHE_SIZE = 10


def get_parser():
    ''' Parse command-line arguments using argparse library '''
    parser = argp.ArgumentParser(
        description='a command-line web scraping tool')
    parser.add_argument('urls', type=str, nargs='*',
                        help='URLs/files to scrape')
    parser.add_argument('-a', '--attributes', type=str, nargs='*',
                        help='extract text using tag attributes')
    parser.add_argument('-c', '--crawl', type=str, nargs='*',
                        help='regexp rules for following new pages')
    parser.add_argument('-ca', '--crawl-all', help='crawl all pages',
                        action='store_true')
    parser.add_argument('-f', '--filter', type=str, nargs='*',
                        help='regexp rules for filtering text')
    parser.add_argument('-ht', '--html', help='write pages as HTML',
                        action='store_true')
    parser.add_argument('-mp', '--maxpages', type=int,
                        help='max number of pages to crawl')
    parser.add_argument('-ml', '--maxlinks', type=int,
                        help='max number of links to scrape')
    parser.add_argument('-n', '--nonstrict', action='store_true',
                        help='allow crawler to visit any domain')
    parser.add_argument('-p', '--pdf', help='write pages as pdf',
                        action='store_true')
    parser.add_argument('-q', '--quiet', help='suppress program output',
                        action='store_true')
    parser.add_argument('-t', '--text', help='write pages as text (default)',
                        action='store_true')
    parser.add_argument('-v', '--version', help='display current version',
                        action='store_true')
    return parser


def follow_links(args, uncrawled_links, crawled_links, base_url):
    ''' Follow links that have not been crawled yet '''
    crawled_ct = 1
    link_cache = []
    try:
        while uncrawled_links:
            ''' Check limit on number of links and pages to crawl '''
            if ((args['maxlinks'] and
                 len(crawled_links) >= args['maxlinks']) or
                    (args['maxpages'] and crawled_ct >= args['maxpages'])):
                break

            ''' Find the next uncrawled link and crawl it '''
            url = uncrawled_links.pop(last=False)

            ''' Compare scheme-less URLs to prevent http(s):// dupes '''
            if (utils.check_scheme(url) and
                    utils.remove_scheme(url) not in crawled_links):
                raw_html = utils.get_raw_html(url)
                if raw_html is not None:
                    html = lh.fromstring(raw_html)
                    ''' Compute a hash of the page
                        Check if it is in the page cache
                    '''
                    page_text = utils.filter_text(html)
                    link_hash = utils.hash_text(''.join(page_text))

                    ''' Ignore page if found in cache, otherwise add it '''
                    if link_hash in link_cache:
                        continue

                    utils.cache_link(link_cache, link_hash, LINK_CACHE_SIZE)

                    ''' Find and clean new links available on page
                        and add to the crawled pages count
                    '''
                    links = [utils.clean_url(u, base_url) for u in
                             html.xpath('//a/@href')]
                    crawled_ct += 1

                    ''' Check for keywords to follow links by '''
                    if args['crawl']:
                        for keyword in args['crawl']:
                            links = utils.filter_re(links, keyword)

                    ''' Domain may be restricted to the seed domain '''
                    if not args['nonstrict'] and args['domain'] in url:
                        links = [x for x in links if args['domain'] in x]

                    ''' Update uncrawled links with new links
                        add scheme-less URL to crawled links
                        write_part_file creates a temporary
                        PART.html file to be processed in
                        write_pages
                    '''
                    uncrawled_links.update(links)
                    crawled_links.add(utils.remove_scheme(url))
                    utils.write_part_file(raw_html, len(crawled_links))
                    if not args['quiet']:
                        print('Crawled {0} (#{1}).'
                              .format(url, len(crawled_links)))
                else:
                    if not args['quiet']:
                        sys.stderr.write('Failed to parse {0}.\n'
                                         .format(url))
    except KeyboardInterrupt:
        pass


def crawl(args, base_url):
    ''' Find links given a seed URL and follow them breadth-first '''
    crawled_links = set()
    uncrawled_links = OrderedSet()

    raw_html = utils.get_raw_html(base_url)
    if raw_html is not None:
        html = lh.fromstring(raw_html)

        ''' Remove URL fragments and append base url if domain is missing '''
        links = [utils.clean_url(u, base_url) for u
                 in html.xpath('//a/@href')]

        ''' Domain may be restricted to the seed domain '''
        if not args['nonstrict']:
            links = [x for x in links if args['domain'] in x]

        ''' Links may have keywords to follow them by '''
        if args['crawl']:
            for keyword in args['crawl']:
                links = [x for x in links if keyword in x]

        ''' Update uncrawled links with new links
            add scheme-less URL to crawled links
            write_part_file creates a temporary PART.html file
            to be processed in write_pages
        '''
        uncrawled_links.update(links)
        crawled_links.add(utils.remove_scheme(base_url))
        utils.write_part_file(raw_html, len(crawled_links))
        if not args['quiet']:
            print('Crawled {0} (#{1}).'.format(base_url, len(crawled_links)))

        follow_links(args, uncrawled_links, crawled_links, base_url)

    return list(crawled_links)


def pdfkit_convert(args, in_files, out_file_names):
    ''' Attempt file conversion to pdf using pdfkit '''
    options = {}

    ''' Only ignore errors if there is more than one page
        This prevents an empty write if an error occurs
    '''
    if len(in_files) > 1:
        options['ignore-load-errors'] = None

    if args['quiet']:
        options['quiet'] = None
    else:
        if not args['local']:
            print('Attempting to write {0} page(s) to {1}.'
                  .format(len(in_files), out_file_names[0]))

    try:
        if args['local']:
            for i, in_file in enumerate(in_files):
                if not args['quiet']:
                    print('Attempting to write to {0}.'
                          .format(out_file_names[i]))
                pk.from_file(in_file, out_file_names[i], options=options)
        else:
            pk.from_file(in_files, out_file_names[0], options=options)
    except (KeyboardInterrupt, Exception) as err:
        if not args['local']:
            ''' Remove PART.html files '''
            utils.remove_part_files()
        raise err


def write_to_pdf(args, in_files, out_file_name, filtering_html):
    ''' Write pages to pdf '''
    if not filtering_html:
        sys.stderr.write('Only HTML can be converted to pdf.\n')
        return False

    if isinstance(out_file_name, list):
        out_file_names = [x + '.pdf' for x in out_file_name]
        for f_name in out_file_names:
            utils.remove_file(f_name)
        pdfkit_convert(args, in_files, out_file_names)
    else:
        out_file_name = out_file_name + '.pdf'
        utils.remove_file(out_file_name)
        pdfkit_convert(args, in_files, [out_file_name])


def write_to_text(args, in_files, out_file_name, filtering_html):
    ''' Write pages to text '''
    if args['local']:
        ''' Write input files to multiple text files '''
        out_file_names = [x + '.txt' for x in out_file_name]
    else:
        ''' Write PART files to a single text file '''
        out_file_name = out_file_name + '.txt'

        if not args['quiet']:
            print('Attempting to write {0} page(s) to {1}.'
                  .format(len(in_files), out_file_name))

    for i, in_file in enumerate(in_files):
        if filtering_html:
            ''' Read a single HTML file and convert it to an lxml object '''
            html = lh.fromstring(utils.read_files(in_file).next())
            text = None
        else:
            html = None
            text = in_file

        if html is not None:
            text = utils.filter_text(html, args['filter'], args['attributes'])
        elif text is not None:
            text = utils.filter_text(text, args['filter'], filter_html=False)
        else:
            if not args['quiet']:
                if args['local']:
                    sys.stderr.write('Failed to parse file {0}.\n'
                                     .format(out_file_names[i].replace(
                                         '.txt', '.html')))
                else:
                    sys.stderr.write('Failed to parse part file {0}.\n'
                                     .format(i+1))

        if text:
            if args['local']:
                if not args['quiet']:
                    print('Attempting to write to {0}.'
                          .format(out_file_names[i]))
                utils.remove_file(out_file_names[i])
                utils.write_file(text, out_file_names[i])
            else:
                utils.remove_file(out_file_name)
                utils.write_file(text, out_file_name)


def write_pages(args, file_names, out_file_name):
    ''' Write scraped pages or user-inputted files to text or pdf '''
    filtering_html = False
    if args['local']:
        ''' If user enters any HTML files then set filter for HTML '''
        ''' Check whether user is filtering text or html '''
        if any('.html' in x for x in file_names):
            filtering_html = True

        ''' Converting to pdf requires filenames, not file contents '''
        if args['pdf']:
            in_files = file_names
        else:
            in_files = utils.read_files(file_names)
    else:
        ''' Scraped URLs are downloaded as HTML files '''
        filtering_html = True
        in_files = utils.get_part_filenames(len(file_names))

    if args['pdf']:
        write_to_pdf(args, in_files, out_file_name, filtering_html)
    else:
        write_to_text(args, in_files, out_file_name, filtering_html)
    if not args['local']:
        ''' Remove PART.html files '''
        utils.remove_part_files()


def scrape(args):
    ''' Extract, filter, and convert webpages to text, pdf, or HTML files '''
    try:
        base_dir = os.getcwd()

        ''' Check if local files entered instead of URLs '''
        args['local'] = None
        for arg_url in args['urls']:
            if os.path.isfile(arg_url):
                args['local'] = args['urls']

        ''' Avoid converting local files to HTML, currently does nothing '''
        if args['local'] and args['html']:
            sys.stderr.write('Cannot convert local files to HTML.\n')
            return False

        ''' Read in local files '''
        if args['local']:
            pages = []
            out_files = []
            for f_name in args['local']:
                if os.path.isfile(f_name):
                    ''' The proper file extension is added in write_pages '''
                    out_files.append('.'.join(f_name.split('.')[:-1]))
                    pages.append(f_name)
                else:
                    sys.stderr.write('{0} was not found.\n'.format(f_name))
                    return False
            write_pages(args, pages, out_files)
        else:
            ''' Scrape URLs '''
            for arg_url in args['urls']:
                url = utils.add_url_ext(arg_url)

                ''' Add http:// scheme if none found '''
                if not utils.check_scheme(url):
                    url = utils.add_scheme(url)

                domain = utils.get_domain(url)
                args['domain'] = domain

                if args['html']:
                    ''' Save .html files in a subdir named after the domain '''
                    if not args['quiet']:
                        print('Storing html files in {0}/'.format(domain))
                    utils.mkdir_and_cd(domain)

                if args['crawl'] or args['crawl_all']:
                    ''' crawl traverses and saves pages as PART.html files '''
                    pages = crawl(args, url)
                else:
                    pages = [url]
                    raw_html = utils.get_raw_html(url)
                    if raw_html is not None:
                        utils.write_part_file(raw_html, len(pages))
                    else:
                        return False

                if args['html']:
                    ''' Return to base directory, files have been written '''
                    os.chdir(base_dir)
                else:
                    ''' Write pages to text or pdf '''
                    ''' The proper file extension is added in write_pages '''
                    out_file = utils.get_out_filename(url, domain)
                    write_pages(args, pages, out_file)

    except (KeyboardInterrupt, Exception) as err:
        if args['html']:
            ''' Return to base directory '''
            try:
                os.chdir(base_dir)
            except OSError:
                pass
        else:
            ''' Remove PART.html files '''
            utils.remove_part_files()
        raise err


def command_line_runner():
    ''' Handle command-line interaction '''
    parser = get_parser()
    args = vars(parser.parse_args())

    if args['version']:
        print(__version__)
        return

    if not args['urls']:
        parser.print_help()
        return

    if not args['text'] and not args['pdf'] and not args['html']:
        valid_types = ['text', 'pdf', 'html']
        try:
            file_type = input('Save output as ({0}): '
                              .format(', '.join(valid_types))).lower()
            while file_type not in valid_types:
                file_type = input('Invalid entry. Choose from ({0}): '
                                  .format(', '.join(valid_types))).lower()
        except KeyboardInterrupt:
            return
        args[file_type] = True

    scrape(args)


if __name__ == '__main__':
    command_line_runner()
