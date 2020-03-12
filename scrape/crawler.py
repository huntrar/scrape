"""A class to crawl webpages."""

from __future__ import absolute_import, print_function
import sys

import lxml.html as lh

from .orderedset import OrderedSet
from . import utils


class Crawler(object):
    """Follows and saves webpages to PART.html files."""

    def __init__(self, args, seed_url=None):
        """Set seed URL and program arguments"""
        self.seed_url = seed_url
        self.args = args
        self.page_cache = []

    def get_new_links(self, url, resp):
        """Get new links from a URL and filter them."""
        links_on_page = resp.xpath("//a/@href")
        links = [utils.clean_url(u, url) for u in links_on_page]

        # Remove non-links through filtering by protocol
        links = [x for x in links if utils.check_protocol(x)]

        # Restrict new URLs by the domain of the input URL
        if not self.args["nonstrict"]:
            domain = utils.get_domain(url)
            links = [x for x in links if utils.get_domain(x) == domain]

        # Filter URLs by regex keywords, if any
        if self.args["crawl"]:
            links = utils.re_filter(links, self.args["crawl"])
        return links

    def limit_reached(self, num_crawls):
        """Check if number of pages crawled have reached a limit."""
        return self.args["max_crawls"] and num_crawls >= self.args["max_crawls"]

    def page_crawled(self, page_resp):
        """Check if page has been crawled by hashing its text content.

        Add new pages to the page cache.
        Return whether page was found in cache.
        """
        page_text = utils.parse_text(page_resp)
        page_hash = utils.hash_text("".join(page_text))
        if page_hash not in self.page_cache:
            utils.cache_page(self.page_cache, page_hash, self.args["cache_size"])
            return False
        return True

    def crawl_links(self, seed_url=None):
        """Find new links given a seed URL and follow them breadth-first.

        Save page responses as PART.html files.
        Return the PART.html filenames created during crawling.
        """
        if seed_url is not None:
            self.seed_url = seed_url

        if self.seed_url is None:
            sys.stderr.write("Crawling requires a seed URL.\n")
            return []

        prev_part_num = utils.get_num_part_files()
        crawled_links = set()
        uncrawled_links = OrderedSet()

        uncrawled_links.add(self.seed_url)
        try:
            while uncrawled_links:
                # Check limit on number of links and pages to crawl
                if self.limit_reached(len(crawled_links)):
                    break
                url = uncrawled_links.pop(last=False)

                # Remove protocol, fragments, etc. to get unique URLs
                unique_url = utils.remove_protocol(utils.clean_url(url))
                if unique_url not in crawled_links:
                    raw_resp = utils.get_raw_resp(url)
                    if raw_resp is None:
                        if not self.args["quiet"]:
                            sys.stderr.write("Failed to parse {0}.\n".format(url))
                        continue

                    resp = lh.fromstring(raw_resp)
                    if self.page_crawled(resp):
                        continue

                    crawled_links.add(unique_url)
                    new_links = self.get_new_links(url, resp)
                    uncrawled_links.update(new_links)
                    if not self.args["quiet"]:
                        print("Crawled {0} (#{1}).".format(url, len(crawled_links)))

                    # Write page response to PART.html file
                    utils.write_part_file(
                        self.args, url, raw_resp, resp, len(crawled_links)
                    )
        except (KeyboardInterrupt, EOFError):
            pass

        curr_part_num = utils.get_num_part_files()
        return utils.get_part_filenames(curr_part_num, prev_part_num)
