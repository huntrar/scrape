#!/usr/bin/env python
""" scrape - a command-line web scraping tool

    written by Hunter Hammond (huntrar@gmail.com)
"""

from __future__ import absolute_import, print_function
from argparse import ArgumentParser
import os
import sys

from scrape import utils
from scrape.crawler import Crawler
from scrape import __version__


def get_parser():
    """Parse command-line arguments."""
    parser = ArgumentParser(description='a command-line web scraping tool')
    parser.add_argument('query', metavar='QUERY', type=str, nargs='*',
                        help='URL\'s/files to scrape')
    parser.add_argument('-a', '--attributes', type=str, nargs='*',
                        help='extract text using tag attributes')
    parser.add_argument('-all', '--crawl-all', help='crawl all pages',
                        action='store_true')
    parser.add_argument('-c', '--crawl', type=str, nargs='*',
                        help='regexp rules for following new pages')
    parser.add_argument('-C', '--clear-cache', help='clear requests cache',
                        action='store_true')
    parser.add_argument('--csv', help='write files as csv',
                        action='store_true')
    parser.add_argument('-cs', '--cache-size', type=int, nargs='?',
                        help='size of page cache (default: 1000)',
                        default=1000)
    parser.add_argument('-f', '--filter', type=str, nargs='*',
                        help='regexp rules for filtering text')
    parser.add_argument('--html', help='write files as HTML',
                        action='store_true')
    parser.add_argument('-i', '--images', action='store_true',
                        help='save page images')
    parser.add_argument('-m', '--multiple', help='save to multiple files',
                        action='store_true')
    parser.add_argument('-max', '--max-crawls', type=int,
                        help='max number of pages to crawl')
    parser.add_argument('-n', '--nonstrict', action='store_true',
                        help='allow crawler to visit any domain')
    parser.add_argument('-ni', '--no-images', action='store_true',
                        help='do not save page images')
    parser.add_argument('-no', '--no-overwrite', action='store_true',
                        help='do not overwrite files if they exist')
    parser.add_argument('-o', '--out', type=str, nargs='*',
                        help='specify outfile names')
    parser.add_argument('-ow', '--overwrite', action='store_true',
                        help='overwrite a file if it exists')
    parser.add_argument('-p', '--pdf', help='write files as pdf',
                        action='store_true')
    parser.add_argument('-pt', '--print', help='print text output',
                        action='store_true')
    parser.add_argument('-q', '--quiet', help='suppress program output',
                        action='store_true')
    parser.add_argument('-s', '--single', help='save to a single file',
                        action='store_true')
    parser.add_argument('-t', '--text', help='write files as text',
                        action='store_true')
    parser.add_argument('-v', '--version', help='display current version',
                        action='store_true')
    parser.add_argument('-x', '--xpath', type=str, nargs='?',
                        help='filter HTML using XPath')
    return parser


def print_text(args, infilenames):
    """Print text content of infiles to stdout.

    Keyword arguments:
    args -- program arguments (dict)
    infilenames -- names of user-inputted and/or downloaded files (list)
    """
    for infilename in infilenames:
        parsed_text = utils.get_parsed_text(args, infilename)
        if parsed_text:
            for line in parsed_text:
                print(line)
            print('')


def write_files(args, infilenames, outfilename):
    """Write scraped or local file(s) in desired format.

    Keyword arguments:
    args -- program arguments (dict)
    infilenames -- names of user-inputted and/or downloaded files (list)
    outfilename -- name of output file (str)

    Remove PART(#).html files after conversion unless otherwise specified.
    """
    try:
        if args['print']:
            print_text(args, infilenames)
        elif args['pdf']:
            if not outfilename.endswith('.pdf'):
                outfilename = outfilename + '.pdf'
            utils.write_pdf_files(args, infilenames, outfilename)
        elif args['csv']:
            # csv/text is parsed by XPath/regexes/tag attributes prior to writing
            if not outfilename.endswith('.csv'):
                outfilename = outfilename + '.csv'
            utils.write_csv_files(args, infilenames, outfilename)
        elif args['text']:
            if not outfilename.endswith('.txt'):
                outfilename = outfilename + '.txt'
            utils.write_text_files(args, infilenames, outfilename)
    except (KeyboardInterrupt, Exception):
        if args['urls'] and not args['html']:
            utils.remove_part_files()
        raise

    if args['urls'] and not args['html']:
        utils.remove_part_files()


def get_single_outfilename(args):
    """Use first possible entry in query as filename."""
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
    """Write to a single output file and/or subdirectory."""
    crawler = Crawler(args)

    if args['urls']:
        domain = utils.get_domain(args['urls'][0])
        if args['html']:
            # Create a single directory to store HTML files in
            if not args['quiet']:
                print('Storing html files in {0}/'.format(domain))
            utils.mkdir_and_cd(domain)

    infilenames = []
    for query in args['query']:
        if query.strip('/') in args['urls']:
            if args['crawl'] or args['crawl_all']:
                # Crawl and/or write HTML files and possibly images to disk
                infilenames += crawler.crawl_links(query)
            else:
                raw_resp = utils.get_raw_resp(query)
                if raw_resp is not None:
                    prev_part_num = utils.get_num_part_files()
                    utils.write_part_file(args, query, raw_resp)
                    curr_part_num = prev_part_num + 1
                    infilenames += utils.get_part_filenames(curr_part_num,
                                                            prev_part_num)
                else:
                    return False
        elif query in args['files']:
            infilenames.append(query)

    if args['html']:
        # HTML files have been written already, so return to base directory
        os.chdir(base_dir)
    else:
        # Write files to text or pdf
        if infilenames:
            if args['out']:
                outfilename = args['out'][0]
            else:
                outfilename = get_single_outfilename(args)
            if outfilename:
                write_files(args, infilenames, outfilename)
        else:
            utils.remove_part_files()
    return True


def write_multiple_files(args, base_dir):
    """Write to multiple output files and/or subdirectories."""
    crawler = Crawler(args)

    for i, query in enumerate(args['query']):
        if query in args['files']:
            # Write files
            if args['out'] and i < len(args['out']):
                outfilename = args['out'][i]
            else:
                outfilename = '.'.join(query.split('.')[:-1])
            write_files(args, [query], outfilename)
        elif query in args['urls']:
            # Scrape/crawl urls
            domain = utils.get_domain(query)
            if args['html']:
                # Save .html files in a subdir named after the domain
                if not args['quiet']:
                    print('Storing html files in {0}/'.format(domain))
                utils.mkdir_and_cd(domain)

            # Crawl and/or write HTML files and possibly images to disk
            if args['crawl'] or args['crawl_all']:
                # Traverses and saves pages as PART.html files
                infilenames = crawler.crawl_links(query)
            else:
                raw_resp = utils.get_raw_resp(query)
                if raw_resp is not None:
                    # Saves page as PART.html file
                    prev_part_num = utils.get_num_part_files()
                    utils.write_part_file(args, query, raw_resp)
                    curr_part_num = prev_part_num + 1
                    infilenames = utils.get_part_filenames(curr_part_num,
                                                           prev_part_num)
                else:
                    return False

            if args['html']:
                # HTML files have been written already, so return to base dir
                os.chdir(base_dir)
            else:
                # Write files to text or pdf
                if infilenames:
                    if args['out'] and i < len(args['out']):
                        outfilename = args['out'][i]
                    else:
                        outfilename = utils.get_outfilename(query, domain)
                    write_files(args, infilenames, outfilename)
                else:
                    sys.stderr.write('Failed to retrieve content from {0}.\n'
                                     .format(query))
    return True


def scrape(args):
    """Extract, filter, and convert webpages to text, pdf, or HTML files."""
    try:
        base_dir = os.getcwd()

        if args['out'] is None:
            args['out'] = []

        # Detect whether to save to a single or multiple files
        if not args['single'] and not args['multiple']:
            # Save to multiple files if multiple files/URL's entered
            if len(args['query']) > 1 or len(args['out']) > 1:
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
                args['urls'].append(arg.strip('/'))

        if args['urls']:
            # Add URL extensions and schemes and update query and URL's
            urls_with_exts = [utils.add_url_suffix(x) for x in args['urls']]
            args['query'] = [utils.add_protocol(x) if x in args['urls']
                             and not utils.check_protocol(x) else x
                             for x in urls_with_exts]
            args['urls'] = [x for x in args['query'] if x not in args['files']]

        # Print error if attempting to convert local files to HTML
        if args['files'] and args['html']:
            sys.stderr.write('Cannot convert local files to HTML.\n')
            args['files'] = []

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
    """Handle command-line interaction."""
    parser = get_parser()
    args = vars(parser.parse_args())
    if args['version']:
        print(__version__)
        return
    if args['clear_cache']:
        utils.clear_cache()
        print('Cleared {0}.'.format(utils.CACHE_DIR))
        return
    if not args['query']:
        parser.print_help()
        return

    # Enable cache unless user sets environ variable SCRAPE_DISABLE_CACHE
    if not os.getenv('SCRAPE_DISABLE_CACHE'):
        utils.enable_cache()

    # Prompt user for filetype if none specified
    valid_types = ('print', 'text', 'csv', 'pdf', 'html')
    if not any(args[x] for x in valid_types):
        try:
            filetype = input('Print or save output as ({0}): '
                             .format(', '.join(valid_types))).lower()
            while filetype not in valid_types:
                filetype = input('Invalid entry. Choose from ({0}): '
                                 .format(', '.join(valid_types))).lower()
        except (KeyboardInterrupt, EOFError):
            return
        args[filetype] = True

    # Save images unless uset sets environ variable SCRAPE_DISABLE_IMGS
    if os.getenv('SCRAPE_DISABLE_IMGS'):
        args['no_images'] = True

    # Ask user if they want to save images when crawling due to its overhead
    # This is only applicable when saving to pdf or HTML formats
    if (args['pdf'] or args['html']) and (args['crawl'] or args['crawl_all']):
        if not args['images'] and not args['no_images']:
            save_msg = ('Choosing to save images will greatly slow the'
                        ' crawling process.\nSave images anyways? (y/n): ')
            try:
                save_images = utils.confirm_input(input(save_msg))
            except (KeyboardInterrupt, EOFError):
                return
            if save_images:
                args['images'] = True
                args['no_images'] = False
            else:
                args['no_images'] = True
                args['images'] = False

    scrape(args)


if __name__ == '__main__':
    command_line_runner()
