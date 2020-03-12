#!/usr/bin/env python
""" scrape - a command-line web scraping tool

    written by Hunter Hammond (huntrar@gmail.com)
"""

from __future__ import absolute_import, print_function
from argparse import ArgumentParser
import os
import sys

from six.moves import input
from six import iterkeys

from .crawler import Crawler
from . import utils, __version__


def get_parser():
    """Parse command-line arguments."""
    parser = ArgumentParser(description="a command-line web scraping tool")
    parser.add_argument(
        "query", metavar="QUERY", type=str, nargs="*", help="URLs/files to scrape"
    )
    parser.add_argument(
        "-a",
        "--attributes",
        type=str,
        nargs="*",
        help="extract text using tag attributes",
    )
    parser.add_argument(
        "-all", "--crawl-all", help="crawl all pages", action="store_true"
    )
    parser.add_argument(
        "-c",
        "--crawl",
        type=str,
        nargs="*",
        help="regexp rules for following new pages",
    )
    parser.add_argument(
        "-C", "--clear-cache", help="clear requests cache", action="store_true"
    )
    parser.add_argument("--csv", help="write files as csv", action="store_true")
    parser.add_argument(
        "-cs",
        "--cache-size",
        type=int,
        nargs="?",
        help="size of page cache (default: 1000)",
        default=1000,
    )
    parser.add_argument(
        "-f", "--filter", type=str, nargs="*", help="regexp rules for filtering text"
    )
    parser.add_argument("--html", help="write files as HTML", action="store_true")
    parser.add_argument("-i", "--images", action="store_true", help="save page images")
    parser.add_argument(
        "-m", "--multiple", help="save to multiple files", action="store_true"
    )
    parser.add_argument(
        "-max", "--max-crawls", type=int, help="max number of pages to crawl"
    )
    parser.add_argument(
        "-n",
        "--nonstrict",
        action="store_true",
        help="allow crawler to visit any domain",
    )
    parser.add_argument(
        "-ni", "--no-images", action="store_true", help="do not save page images"
    )
    parser.add_argument(
        "-no",
        "--no-overwrite",
        action="store_true",
        help="do not overwrite files if they exist",
    )
    parser.add_argument(
        "-o", "--out", type=str, nargs="*", help="specify outfile names"
    )
    parser.add_argument(
        "-ow", "--overwrite", action="store_true", help="overwrite a file if it exists"
    )
    parser.add_argument("-p", "--pdf", help="write files as pdf", action="store_true")
    parser.add_argument("-pt", "--print", help="print text output", action="store_true")
    parser.add_argument(
        "-q", "--quiet", help="suppress program output", action="store_true"
    )
    parser.add_argument(
        "-s", "--single", help="save to a single file", action="store_true"
    )
    parser.add_argument("-t", "--text", help="write files as text", action="store_true")
    parser.add_argument(
        "-v", "--version", help="display current version", action="store_true"
    )
    parser.add_argument(
        "-x", "--xpath", type=str, nargs="?", help="filter HTML using XPath"
    )
    return parser


def write_files(args, infilenames, outfilename):
    """Write scraped or local file(s) in desired format.

    Keyword arguments:
    args -- program arguments (dict)
    infilenames -- names of user-inputted and/or downloaded files (list)
    outfilename -- name of output file (str)

    Remove PART(#).html files after conversion unless otherwise specified.
    """
    write_actions = {
        "print": utils.print_text,
        "pdf": utils.write_pdf_files,
        "csv": utils.write_csv_files,
        "text": utils.write_text_files,
    }
    try:
        for action in iterkeys(write_actions):
            if args[action]:
                write_actions[action](args, infilenames, outfilename)
    finally:
        if args["urls"] and not args["html"]:
            utils.remove_part_files()


def write_single_file(args, base_dir, crawler):
    """Write to a single output file and/or subdirectory."""
    if args["urls"] and args["html"]:
        # Create a directory to save PART.html files in
        domain = utils.get_domain(args["urls"][0])
        if not args["quiet"]:
            print("Storing html files in {0}/".format(domain))
        utils.mkdir_and_cd(domain)

    infilenames = []
    for query in args["query"]:
        if query in args["files"]:
            infilenames.append(query)
        elif query.strip("/") in args["urls"]:
            if args["crawl"] or args["crawl_all"]:
                # Crawl and save HTML files/image files to disk
                infilenames += crawler.crawl_links(query)
            else:
                raw_resp = utils.get_raw_resp(query)
                if raw_resp is None:
                    return False

                prev_part_num = utils.get_num_part_files()
                utils.write_part_file(args, query, raw_resp)
                curr_part_num = prev_part_num + 1
                infilenames += utils.get_part_filenames(curr_part_num, prev_part_num)

    # Convert output or leave as PART.html files
    if args["html"]:
        # HTML files have been written already, so return to base directory
        os.chdir(base_dir)
    else:
        # Write files to text or pdf
        if infilenames:
            if args["out"]:
                outfilename = args["out"][0]
            else:
                outfilename = utils.get_single_outfilename(args)
            if outfilename:
                write_files(args, infilenames, outfilename)
        else:
            utils.remove_part_files()
    return True


def write_multiple_files(args, base_dir, crawler):
    """Write to multiple output files and/or subdirectories."""
    for i, query in enumerate(args["query"]):
        if query in args["files"]:
            # Write files
            if args["out"] and i < len(args["out"]):
                outfilename = args["out"][i]
            else:
                outfilename = ".".join(query.split(".")[:-1])
            write_files(args, [query], outfilename)
        elif query in args["urls"]:
            # Scrape/crawl urls
            domain = utils.get_domain(query)
            if args["html"]:
                # Create a directory to save PART.html files in
                if not args["quiet"]:
                    print("Storing html files in {0}/".format(domain))
                utils.mkdir_and_cd(domain)

            if args["crawl"] or args["crawl_all"]:
                # Crawl and save HTML files/image files to disk
                infilenames = crawler.crawl_links(query)
            else:
                raw_resp = utils.get_raw_resp(query)
                if raw_resp is None:
                    return False

                # Saves page as PART.html file
                prev_part_num = utils.get_num_part_files()
                utils.write_part_file(args, query, raw_resp)
                curr_part_num = prev_part_num + 1
                infilenames = utils.get_part_filenames(curr_part_num, prev_part_num)

            # Convert output or leave as PART.html files
            if args["html"]:
                # HTML files have been written already, so return to base dir
                os.chdir(base_dir)
            else:
                # Write files to text or pdf
                if infilenames:
                    if args["out"] and i < len(args["out"]):
                        outfilename = args["out"][i]
                    else:
                        outfilename = utils.get_outfilename(query, domain)
                    write_files(args, infilenames, outfilename)
                else:
                    sys.stderr.write(
                        "Failed to retrieve content from {0}.\n".format(query)
                    )
    return True


def split_input(args):
    """Split query input into local files and URLs."""
    args["files"] = []
    args["urls"] = []
    for arg in args["query"]:
        if os.path.isfile(arg):
            args["files"].append(arg)
        else:
            args["urls"].append(arg.strip("/"))


def detect_output_type(args):
    """Detect whether to save to a single or multiple files."""
    if not args["single"] and not args["multiple"]:
        # Save to multiple files if multiple files/URLs entered
        if len(args["query"]) > 1 or len(args["out"]) > 1:
            args["multiple"] = True
        else:
            args["single"] = True


def scrape(args):
    """Scrape webpage content."""
    try:
        base_dir = os.getcwd()
        if args["out"] is None:
            args["out"] = []

        # Detect whether to save to a single or multiple files
        detect_output_type(args)

        # Split query input into local files and URLs
        split_input(args)

        if args["urls"]:
            # Add URL extensions and schemes and update query and URLs
            urls_with_exts = [utils.add_url_suffix(x) for x in args["urls"]]
            args["query"] = [
                utils.add_protocol(x) if x in args["urls"] else x
                for x in urls_with_exts
            ]
            args["urls"] = [x for x in args["query"] if x not in args["files"]]

        # Print error if attempting to convert local files to HTML
        if args["files"] and args["html"]:
            sys.stderr.write("Cannot convert local files to HTML.\n")
            args["files"] = []

        # Instantiate web crawler if necessary
        crawler = None
        if args["crawl"] or args["crawl_all"]:
            crawler = Crawler(args)

        if args["single"]:
            return write_single_file(args, base_dir, crawler)
        elif args["multiple"]:
            return write_multiple_files(args, base_dir, crawler)

    except (KeyboardInterrupt, Exception):
        if args["html"]:
            try:
                os.chdir(base_dir)
            except OSError:
                pass
        else:
            utils.remove_part_files()
        raise


def prompt_filetype(args):
    """Prompt user for filetype if none specified."""
    valid_types = ("print", "text", "csv", "pdf", "html")
    if not any(args[x] for x in valid_types):
        try:
            filetype = input(
                "Print or save output as ({0}): ".format(", ".join(valid_types))
            ).lower()
            while filetype not in valid_types:
                filetype = input(
                    "Invalid entry. Choose from ({0}): ".format(", ".join(valid_types))
                ).lower()
        except (KeyboardInterrupt, EOFError):
            return
        args[filetype] = True


def prompt_save_images(args):
    """Prompt user to save images when crawling (for pdf and HTML formats)."""
    if args["images"] or args["no_images"]:
        return

    if (args["pdf"] or args["html"]) and (args["crawl"] or args["crawl_all"]):
        save_msg = (
            "Choosing to save images will greatly slow the"
            " crawling process.\nSave images anyways? (y/n): "
        )
        try:
            save_images = utils.confirm_input(input(save_msg))
        except (KeyboardInterrupt, EOFError):
            return

        args["images"] = save_images
        args["no_images"] = not save_images


def command_line_runner():
    """Handle command-line interaction."""
    parser = get_parser()
    args = vars(parser.parse_args())
    if args["version"]:
        print(__version__)
        return
    if args["clear_cache"]:
        utils.clear_cache()
        print("Cleared {0}.".format(utils.CACHE_DIR))
        return
    if not args["query"]:
        parser.print_help()
        return

    # Enable cache unless user sets environ variable SCRAPE_DISABLE_CACHE
    if not os.getenv("SCRAPE_DISABLE_CACHE"):
        utils.enable_cache()

    # Save images unless user sets environ variable SCRAPE_DISABLE_IMGS
    if os.getenv("SCRAPE_DISABLE_IMGS"):
        args["no_images"] = True

    # Prompt user for filetype if none specified
    prompt_filetype(args)

    # Prompt user to save images when crawling (for pdf and HTML formats)
    prompt_save_images(args)

    # Scrape webpage content
    scrape(args)


if __name__ == "__main__":
    command_line_runner()
