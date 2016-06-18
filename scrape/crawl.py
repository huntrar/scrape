"""Link crawling functions"""

from __future__ import absolute_import, print_function
import os
import sys

import lxml.html as lh

from scrape.orderedset import OrderedSet
from scrape import utils


def get_links(args, url, resp, domain):
    """Get new links and possibly restrict them by domain"""
    links = [utils.clean_url(u, url) for u
             in resp.xpath('//a/@href')]

    # Restrict domain
    if not args['nonstrict']:
        links = [x for x in links if utils.get_domain(x) == domain]
    return links


def follow_links(args, uncrawled_links, crawled_links, seed_url, seed_domain):
    """Follow links that have not been crawled yet

       Keyword arguments:
       args -- program arguments (dict)
       uncrawled_links -- links to be crawled (OrderedSet)
       crawled_links -- links already crawled (set)
       seed_url -- the first crawled link (str)
       seed_domain -- the domain of the seed URL (str)

       Retrieve HTML from links and write them to PART(#).html files.
    """
    crawled_ct = 1
    link_cache = []
    try:
        while uncrawled_links:
            # Check limit on number of links and pages to crawl
            if ((args['maxlinks'] and
                 len(crawled_links) >= args['maxlinks']) or
                    (args['maxpages'] and crawled_ct >= args['maxpages'])):
                break

            url = uncrawled_links.pop(last=False)

            # Compare scheme-less URLs to prevent http(s):// dupes
            clean_url = utils.remove_scheme(utils.clean_url(url))
            if clean_url not in crawled_links:
                raw_resp = utils.get_raw_resp(url)
                if raw_resp is not None:
                    resp = lh.fromstring(raw_resp)

                    # Compute a hash of the page and check if it is in cache
                    page_text = utils.parse_text(resp)
                    link_hash = utils.hash_text(''.join(page_text))
                    if link_hash in link_cache:
                        continue
                    utils.cache_link(link_cache, link_hash, args['cache_size'])

                    # Find new links and remove fragments/append base url
                    # if necessary
                    crawled_ct += 1
                    links = get_links(args, seed_url, resp, seed_domain)

                    # Links may be filtered by regex keywords
                    if args['crawl']:
                        links = utils.re_filter(links, args['crawl'])

                    uncrawled_links.update(links)
                    crawled_links.add(clean_url)
                    utils.write_part_file(args, url, raw_resp, resp,
                                          len(crawled_links))
                    if not args['quiet']:
                        print('Crawled {0} (#{1}).'
                              .format(url, len(crawled_links)))
                else:
                    if not args['quiet']:
                        sys.stderr.write('Failed to parse {0}.\n'
                                         .format(url))
    except (KeyboardInterrupt, EOFError):
        pass


def crawl(args, seed_url, seed_domain):
    """Find links given a seed URL and follow them breadth-first

       Keyword arguments:
       args -- program arguments (dict)
       seed_url -- the first link to crawl (str)
       seed_domain -- the domain of the seed URL (str)

       Initialize crawled/uncrawled links by exctracting links from a seed URL.
       Returns the PART.html filenames created during crawling.
    """
    prev_part_num = utils.get_num_part_files()
    crawled_links = set()
    uncrawled_links = OrderedSet()
    raw_resp = utils.get_raw_resp(seed_url)
    if raw_resp is not None:
        resp = lh.fromstring(raw_resp)
        links = get_links(args, seed_url, resp, seed_domain)

        # Links may be filtered by regex keywords
        if args['crawl']:
            for keyword in args['crawl']:
                links = [x for x in links if keyword in x]

        uncrawled_links.update(links)
        crawled_links.add(utils.remove_scheme(utils.clean_url(seed_url)))
        utils.write_part_file(args, seed_url, raw_resp, resp,
                              len(crawled_links))
        if not args['quiet']:
            print('Crawled {0} (#{1}).'.format(seed_url, len(crawled_links)))
        follow_links(args, uncrawled_links, crawled_links, seed_url,
                     seed_domain)
    curr_part_num = utils.get_num_part_files()
    return utils.get_part_filenames(curr_part_num, prev_part_num)
