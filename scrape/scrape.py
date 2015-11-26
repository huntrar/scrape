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

LINK_CACHE_SIZE = 100


def get_parser():
    """Parse command-line arguments using argparse library"""
    parser = argp.ArgumentParser(
        description='a command-line web scraping tool')
    parser.add_argument('query', metavar='QUERY', type=str, nargs='*',
                        help='URL\'s/files to scrape')
    parser.add_argument('-a', '--attributes', type=str, nargs='*',
                        help='extract text using tag attributes')
    parser.add_argument('-c', '--crawl', type=str, nargs='*',
                        help='regexp rules for following new pages')
    parser.add_argument('-ca', '--crawl-all', help='crawl all pages',
                        action='store_true')
    parser.add_argument('-f', '--filter', type=str, nargs='*',
                        help='regexp rules for filtering text')
    parser.add_argument('-ht', '--html', help='write files as HTML',
                        action='store_true')
    parser.add_argument('-m', '--multiple', help='save to multiple files',
                        action='store_true')
    parser.add_argument('-mp', '--maxpages', type=int,
                        help='max number of pages to crawl')
    parser.add_argument('-ml', '--maxlinks', type=int,
                        help='max number of links to scrape')
    parser.add_argument('-n', '--nonstrict', action='store_true',
                        help='allow crawler to visit any domain')
    parser.add_argument('-p', '--pdf', help='write files as pdf',
                        action='store_true')
    parser.add_argument('-q', '--quiet', help='suppress program output',
                        action='store_true')
    parser.add_argument('-s', '--single', help='save to a single file',
                        action='store_true')
    parser.add_argument('-t', '--text', help='write files as text (default)',
                        action='store_true')
    parser.add_argument('-v', '--version', help='display current version',
                        action='store_true')
    parser.add_argument('-x', '--xpath', type=str, nargs='?',
                        help='filter HTML using XPath')
    return parser


def follow_links(args, uncrawled_links, crawled_links, base_url, domain):
    """Follow links that have not been crawled yet"""
    crawled_ct = 1
    link_cache = []
    try:
        while uncrawled_links:
            # Check limit on number of links and pages to crawl
            if ((args['maxlinks'] and
                 len(crawled_links) >= args['maxlinks']) or
                    (args['maxpages'] and crawled_ct >= args['maxpages'])):
                break

            # Find the next uncrawled link and crawl it
            url = uncrawled_links.pop(last=False)

            # Compare scheme-less URLs to prevent http(s):// dupes
            if (utils.check_scheme(url) and
                    utils.remove_scheme(url) not in crawled_links):
                raw_html = utils.get_raw_html(url)
                if raw_html is not None:
                    html = lh.fromstring(raw_html)
                    # Compute a hash of the page and check if it is in
                    #the page cache
                    page_text = utils.parse_text(html)
                    link_hash = utils.hash_text(''.join(page_text))
                    # Ignore page if found in cache, otherwise add it
                    if link_hash in link_cache:
                        continue
                    utils.cache_link(link_cache, link_hash, LINK_CACHE_SIZE)

                    # Find and clean new links available on page and add to the
                    # crawled pages count
                    links = [utils.clean_url(u, base_url) for u in
                             html.xpath('//a/@href')]
                    crawled_ct += 1
                    # Check for keywords to follow links by
                    if args['crawl']:
                        for keyword in args['crawl']:
                            links = utils.re_filter(links, keyword)
                    # Domain may be restricted to the seed domain
                    if not args['nonstrict'] and domain in url:
                        links = [x for x in links if domain in x]

                    # write_part_file creates a temporary PART.html file to be
                    # processed in write_files()
                    uncrawled_links.update(links)
                    crawled_links.add(utils.remove_scheme(url))
                    utils.write_part_file(args, raw_html, len(crawled_links))
                    if not args['quiet']:
                        print('Crawled {0} (#{1}).'
                              .format(url, len(crawled_links)))
                else:
                    if not args['quiet']:
                        sys.stderr.write('Failed to parse {0}.\n'
                                         .format(url))
    except KeyboardInterrupt:
        pass


def crawl(args, base_url, domain):
    """Find links given a seed URL and follow them breadth-first"""
    crawled_links = set()
    uncrawled_links = OrderedSet()

    raw_html = utils.get_raw_html(base_url)
    if raw_html is not None:
        html = lh.fromstring(raw_html)

        # Remove URL fragments and append base url if domain is missing
        links = [utils.clean_url(u, base_url) for u
                 in html.xpath('//a/@href')]
        # Domain may be restricted to the seed domain
        if not args['nonstrict']:
            links = [x for x in links if domain in x]
        # Links may have keywords to follow them by
        if args['crawl']:
            for keyword in args['crawl']:
                links = [x for x in links if keyword in x]

        # write_part_file creates a temporary PART.html file to be
        # processed in write_files()
        uncrawled_links.update(links)
        crawled_links.add(utils.remove_scheme(base_url))
        utils.write_part_file(args, raw_html, len(crawled_links))
        if not args['quiet']:
            print('Crawled {0} (#{1}).'.format(base_url, len(crawled_links)))

        follow_links(args, uncrawled_links, crawled_links, base_url, domain)


def pdfkit_convert_xpath(args, infilenames, outfilenames, options):
    """Filter HTML by XPath before writing to pdf"""
    if args['multiple']:
        html = None
        for i, infilename in enumerate(infilenames):
            if not args['quiet']:
                print('Attempting to write to {0}.'
                      .format(outfilenames[i]))
            else:
                options['quiet'] = None

            html = utils.parse_html(next(utils.read_files(infilename)),
                                    args['xpath'])

            if isinstance(html, list):
                if isinstance(html[0], str):
                    pk.from_string('\n'.join(html), outfilenames[i],
                                   options=options)
                else:
                    pk.from_string('\n'.join(lh.tostring(x) for x in html),
                                   outfilenames[i], options=options)
            elif isinstance(html, str):
                pk.from_string(html, outfilenames[i], options=options)
            else:
                pk.from_string(lh.tostring(html), outfilenames[i],
                               options=options)
    elif args['single']:
        if not args['quiet']:
            print('Attempting to write {0} page(s) to {1}.'
                  .format(len(infilenames), outfilenames[0]))
        else:
            options['quiet'] = None

        html = utils.parse_html(next(utils.read_files(infilenames)),
                                args['xpath'])

        if isinstance(html, list):
            if isinstance(html[0], str):
                pk.from_string('\n'.join(html), outfilenames[0],
                               options=options)
            else:
                pk.from_string('\n'.join(lh.tostring(x) for x in html),
                               outfilenames[0], options=options)
        elif isinstance(html, str):
            pk.from_string(html, outfilenames[0], options=options)
        else:
            pk.from_string(lh.tostring(html), outfilenames[0],
                           options=options)


def pdfkit_convert(args, infilenames, outfilenames):
    """Attempt file conversion to pdf using pdfkit"""
    options = {}

    # Only ignore errors if there is more than one page
    # This prevents an empty write if an error occurs
    if len(infilenames) > 1:
        options['ignore-load-errors'] = None

    try:
        if args['xpath']:
            pdfkit_convert_xpath(args, infilenames, outfilenames, options)
        elif args['multiple']:
            for i, infilename in enumerate(infilenames):
                if not args['quiet']:
                    print('Attempting to write to {0}.'
                          .format(outfilenames[i]))
                else:
                    options['quiet'] = None

                pk.from_file(infilename, outfilenames[i], options=options)
        elif args['single']:
            if not args['quiet']:
                print('Attempting to write {0} page(s) to {1}.'
                      .format(len(infilenames), outfilenames[0]))
            else:
                options['quiet'] = None

            pk.from_file(infilenames, outfilenames[0], options=options)
    except (KeyboardInterrupt, Exception):
        if args['urls']:
            """Remove PART.html files"""
            utils.remove_part_files()
        raise


def write_to_pdf(args, infilenames, outfilenames):
    """Write files to pdf"""
    if args['multiple']:
        pdf_filenames = [x + '.pdf' for x in outfilenames]
        outfilenames = pdf_filenames
        for filename in outfilenames:
            utils.remove_file(filename)
        pdfkit_convert(args, infilenames, outfilenames)
    elif args['single']:
        outfilename = outfilenames[0] + '.pdf'
        utils.remove_file(outfilename)
        pdfkit_convert(args, infilenames, [outfilename])


def write_to_text(args, infilenames, outfilenames):
    """Write files to text"""
    if args['multiple']:
        # Write input files to multiple text files
        txt_filenames = [x + '.txt' for x in outfilenames]
        outfilenames = txt_filenames
    elif args['single']:
        # Aggregate all text for writing to a single output file
        all_text = []

    for i, (infilename, outfilename) in enumerate(zip(infilenames,
                                                        outfilenames)):
        if infilename.endswith('.html'):
            # Convert HTML to lxml object for content parsing
            html = lh.fromstring(next(utils.read_files(infilename)))
            text = None
        else:
            html = None
            text = utils.read_files(infilename)

        if html is not None:
            parsed_text = utils.parse_text(html, args['xpath'], args['filter'],
                                           args['attributes'])
        elif text is not None:
            parsed_text = utils.parse_text(text, args['xpath'], args['filter'])
        else:
            if not args['quiet']:
                if args['files']:
                    sys.stderr.write('Failed to parse file {0}.\n'
                                     .format(outfilename.replace(
                                         '.txt', '.html')))
                else:
                    sys.stderr.write('Failed to parse PART{0}.html.\n'
                                     .format(i + 1))

        if parsed_text:
            if args['multiple']:
                if not args['quiet']:
                    print('Attempting to write to {0}.'
                          .format(outfilename))
                utils.remove_file(outfilename)
                utils.write_file(parsed_text, outfilename)
            elif args['single']:
                all_text += parsed_text

                # Newline added between multiple files being aggregated
                if len(infilenames) > 1 and i < len(infilenames) - 1:
                    all_text.append('\n')

    # Write all text to a single output file
    if args['single'] and all_text:
        outfilename = outfilenames[0] + '.txt'

        if not args['quiet']:
            print('Attempting to write {0} page(s) to {1}.'
                  .format(len(infilenames), outfilename))
        utils.remove_file(outfilename)
        utils.write_file(all_text, outfilename)


def write_files(args, filenames, outfilenames, filetypes):
    """Write scraped pages or user-inputted files to text or pdf"""
    infilenames = []
    if 'files' in filetypes:
        infilenames += filenames

    if 'urls' in filetypes:
        # Scraped URLs are downloaded as PART.html files
        infilenames += utils.get_part_filenames()

    if args['pdf']:
        write_to_pdf(args, infilenames, outfilenames)
    elif args['text']:
        write_to_text(args, infilenames, outfilenames)

    if 'urls' in filetypes and not args['html']:
        utils.remove_part_files()


def get_single_outfilename(args):
    """Use first possible entry in query as filename"""
    for arg in args['query']:
        if arg in args['files']:
            return ('.'.join(arg.split('.')[:-1])).lower()
        for url in args['urls']:
            if arg.strip('/') in url:
                domain = utils.get_domain(url)
                return utils.get_outfilename(url, domain)
    sys.stderr.write('Failed to construct a single out filename.\n')
    return ''


def write_single_file(args, base_dir):
    """Write to a single output file and/or subdirectory"""
    filetypes = []
    filenames = []
    if args['urls']:
        filetypes.append('urls')
        if args['html']:
            # Create a single directory to store HTML files in
            domain = args['domains'][0]
            if not args['quiet']:
                print('Storing html files in {0}/'.format(domain))
            utils.mkdir_and_cd(domain)
    if args['files']:
        filetypes.append('files')
        filenames += list(args['files'])

    for url in args['urls']:
        if args['crawl'] or args['crawl_all']:
            # crawl traverses and saves pages as PART.html files
            crawl(args, url, domain)
        else:
            raw_html = utils.get_raw_html(url)
            if raw_html is not None:
                utils.write_part_file(args, raw_html)
            else:
                return False

    if args['html']:
        # HTML files have been written already, so return to base directory
        os.chdir(base_dir)
    else:
        # Write files to text or pdf
        outfilename = get_single_outfilename(args)
        if outfilename:
            write_files(args, filenames, [outfilename], filetypes)
        else:
            utils.remove_part_files()
    return True


def write_multiple_files(args, base_dir):
    """Write to multiple output files and/or subdirectories"""
    for filename in args['files']:
        filenames = [filename]
        outfilenames = ['.'.join(filename.split('.')[:-1])]
        write_files(args, filenames, outfilenames, ['files'])

    for url, domain in zip(args['urls'], args['domains']):
        if args['html']:
            # Save .html files in a subdir named after the domain
            if not args['quiet']:
                print('Storing html files in {0}/'.format(domain))
            utils.mkdir_and_cd(domain)

        if args['crawl'] or args['crawl_all']:
            # crawl traverses and saves pages as PART.html files
            crawl(args, url, domain)
        else:
            raw_html = utils.get_raw_html(url)
            if raw_html is not None:
                utils.write_part_file(args, raw_html)
            else:
                return False

        if args['html']:
            # HTML files have been written already, so return to base directory
            os.chdir(base_dir)
        else:
            # Write files to text or pdf
            outfilenames = [utils.get_outfilename(url, domain)]
            write_files(args, [], outfilenames, ['urls'])
    return True


def scrape(args):
    """Extract, filter, and convert webpages to text, pdf, or HTML files"""
    try:
        base_dir = os.getcwd()

        # Detect whether to save to a single or multiple files
        if not args['single'] and not args['multiple']:
            # Save to multiple files if multiple files/URL's entered
            if len(args['query']) > 1:
                args['multiple'] = True
            else:
                args['single'] = True

        # Split query input into local files and URL's
        args['files'] = []
        args['urls'] = []
        for arg in args['query']:
            if os.path.isfile(arg):
                args['files'].append(arg)
            else:
                args['urls'].append(arg)

        # Print error if attempting to convert local files to HTML
        if args['files'] and args['html']:
            sys.stderr.write('Cannot convert local files to HTML.\n')
            args['files'] = []

        if args['urls']:
            # Add URL extensions and schemes
            urls_with_exts = [utils.add_url_ext(x) for x in args['urls']]
            args['urls'] = [utils.add_scheme(x) if not utils.check_scheme(x)
                            else x for x in urls_with_exts]
            args['domains'] = [utils.get_domain(x) for x in args['urls']]
        else:
            args['domains'] = []

        if args['single']:
            return write_single_file(args, base_dir)
        elif args['multiple']:
            return write_multiple_files(args, base_dir)
    except (KeyboardInterrupt, Exception):
        if args['html']:
            try:
                os.chdir(base_dir)
            except OSError:
                pass
        else:
            utils.remove_part_files()
        raise


def command_line_runner():
    """Handle command-line interaction"""
    parser = get_parser()
    args = vars(parser.parse_args())

    if args['version']:
        print(__version__)
        return

    if not args['query']:
        parser.print_help()
        return

    if not args['text'] and not args['pdf'] and not args['html']:
        valid_types = ['text', 'pdf', 'html']
        try:
            filetype = input('Save output as ({0}): '
                             .format(', '.join(valid_types))).lower()
            while filetype not in valid_types:
                filetype = input('Invalid entry. Choose from ({0}): '
                                 .format(', '.join(valid_types))).lower()
        except KeyboardInterrupt:
            return
        args[filetype] = True

    scrape(args)


if __name__ == '__main__':
    command_line_runner()
