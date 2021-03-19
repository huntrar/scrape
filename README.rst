scrape |PyPI Version| |Total Downloads|
======================================================

a command-line web scraping tool
--------------------------------

scrape is a rule-based web crawler and information extraction tool
capable of manipulating and merging new and existing documents. XML Path
Language (XPath) and regular expressions are used to define rules for
filtering content and web traversal. Output may be converted into text,
csv, pdf, and/or HTML formats.

Installation
------------

::

    pip install scrape

or

::

    pip install git+https://github.com/huntrar/scrape.git#egg=scrape

or

::

    git clone https://github.com/huntrar/scrape
    cd scrape
    python setup.py install

You must `install
wkhtmltopdf <https://github.com/pdfkit/pdfkit/wiki/Installing-WKHTMLTOPDF>`__
to save files to pdf.

Usage
-----

::

    usage: scrape.py [-h] [-a [ATTRIBUTES [ATTRIBUTES ...]]] [-all]
                     [-c [CRAWL [CRAWL ...]]] [-C] [--csv] [-cs [CACHE_SIZE]]
                     [-f [FILTER [FILTER ...]]] [--html] [-i] [-m]
                     [-max MAX_CRAWLS] [-n] [-ni] [-no] [-o [OUT [OUT ...]]] [-ow]
                     [-p] [-pt] [-q] [-s] [-t] [-v] [-x [XPATH]]
                     [QUERY [QUERY ...]]

    a command-line web scraping tool

    positional arguments:
      QUERY                 URLs/files to scrape

    optional arguments:
      -h, --help            show this help message and exit
      -a [ATTRIBUTES [ATTRIBUTES ...]], --attributes [ATTRIBUTES [ATTRIBUTES ...]]
                            extract text using tag attributes
      -all, --crawl-all     crawl all pages
      -c [CRAWL [CRAWL ...]], --crawl [CRAWL [CRAWL ...]]
                            regexp rules for following new pages
      -C, --clear-cache     clear requests cache
      --csv                 write files as csv
      -cs [CACHE_SIZE], --cache-size [CACHE_SIZE]
                            size of page cache (default: 1000)
      -f [FILTER [FILTER ...]], --filter [FILTER [FILTER ...]]
                            regexp rules for filtering text
      --html                write files as HTML
      -i, --images          save page images
      -m, --multiple        save to multiple files
      -max MAX_CRAWLS, --max-crawls MAX_CRAWLS
                            max number of pages to crawl
      -n, --nonstrict       allow crawler to visit any domain
      -ni, --no-images      do not save page images
      -no, --no-overwrite   do not overwrite files if they exist
      -o [OUT [OUT ...]], --out [OUT [OUT ...]]
                            specify outfile names
      -ow, --overwrite      overwrite a file if it exists
      -p, --pdf             write files as pdf
      -pt, --print          print text output
      -q, --quiet           suppress program output
      -s, --single          save to a single file
      -t, --text            write files as text
      -v, --version         display current version
      -x [XPATH], --xpath [XPATH]
                            filter HTML using XPath

Author
------

-  Hunter Hammond (huntrar@gmail.com)

Notes
-----

-  Input to scrape can be links, files, or a combination of the two,
   allowing you to create new files constructed from both existing and
   newly scraped content.
-  Multiple input files/URLs are saved to multiple output
   files/directories by default. To consolidate them, use the --single
   flag.
-  Images are automatically included when saving as pdf or HTML; this
   involves making additional HTTP requests, adding a significant amount
   of processing time. If you wish to forgo this feature use the
   --no-images flag, or set the environment variable
   SCRAPE\_DISABLE\_IMGS.
-  Requests cache is enabled by default to cache webpages, it can be
   disabled by setting the environment variable SCRAPE\_DISABLE\_CACHE.
-  Pages are saved temporarily as PART.html files during processing.
   Unless saving pages as HTML, these files are removed automatically
   upon conversion or exit.
-  To crawl pages with no restrictions use the --crawl-all flag, or
   filter which pages to crawl by URL keywords by passing one or more
   regexps to --crawl.
-  If you want the crawler to follow links outside of the given URLs
   domain, use --nonstrict.
-  Crawling can be stopped by Ctrl-C or alternatively by setting the
   number of pages or links to be crawled using --maxpages and
   --maxlinks. A page may contain zero or many links to more pages.
-  The text output of scraped files can be printed to stdout rather than
   saved by entering --print.
-  Filtering HTML can be done using --xpath, while filtering text is
   done by entering one or more regexps to --filter.
-  If you only want to specify specific tag attributes to extract rather
   than an entire XPath, use --attributes. The default choice is to
   extract only text attributes, but you can specify one or many
   different attributes (such as href, src, title, or any attribute
   available..).

.. |PyPI Version| image:: https://img.shields.io/pypi/v/scrape.svg
   :target: https://pypi.python.org/pypi/scrape
.. |Total Downloads| image:: https://pepy.tech/badge/scrape
   :target: https://pepy.tech/project/scrape
