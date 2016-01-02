# scrape [![PyPI Version](https://img.shields.io/pypi/v/scrape.svg)](https://pypi.python.org/pypi/scrape) [![Build Status](https://travis-ci.org/huntrar/scrape.svg?branch=master)](https://travis-ci.org/huntrar/scrape) [![PyPI Monthly downloads](https://img.shields.io/pypi/dm/scrape.svg?style=flat)](https://pypi.python.org/pypi/scrape)

## a command-line web scraping tool

scrape is a rule-based web crawler and content extractor which makes web scraping easier than ever. It allows for highly specific queries which make use of regular expressions and the XPath language. Extracted content may be saved and consolidated to text, pdf, or plain HTML.

## Installation
    pip install scrape

or

    pip install git+https://github.com/huntrar/scrape.git#egg=scrape

or

    git clone https://github.com/huntrar/scrape
    cd scrape
    python setup.py install

You must [install wkhtmltopdf](https://github.com/pdfkit/pdfkit/wiki/Installing-WKHTMLTOPDF) to save files to pdf.

## Usage
    usage: scrape.py [-h] [-a [ATTRIBUTES [ATTRIBUTES ...]]]
                     [-c [CRAWL [CRAWL ...]]] [-ca] [-f [FILTER [FILTER ...]]]
                     [-ht] [-m] [-mp MAXPAGES] [-ml MAXLINKS] [-n] [-ni]
                     [-o [OUT [OUT ...]]] [-p] [-q] [-s] [-t] [-v] [-x [XPATH]]
                     [QUERY [QUERY ...]]
    
    a command-line web scraping tool
    
    positional arguments:
      QUERY                 URL's/files to scrape
    
    optional arguments:
      -h, --help            show this help message and exit
      -a [ATTRIBUTES [ATTRIBUTES ...]], --attributes [ATTRIBUTES [ATTRIBUTES ...]]
                            extract text using tag attributes
      -c [CRAWL [CRAWL ...]], --crawl [CRAWL [CRAWL ...]]
                            regexp rules for following new pages
      -ca, --crawl-all      crawl all pages
      -f [FILTER [FILTER ...]], --filter [FILTER [FILTER ...]]
                            regexp rules for filtering text
      -ht, --html           write files as HTML
      -m, --multiple        save to multiple files
      -mp MAXPAGES, --maxpages MAXPAGES
                            max number of pages to crawl
      -ml MAXLINKS, --maxlinks MAXLINKS
                            max number of links to scrape
      -n, --nonstrict       allow crawler to visit any domain
      -ni, --no-images      do not save page images
      -o [OUT [OUT ...]], --out [OUT [OUT ...]]
                            specify outfile names
      -p, --pdf             write files as pdf
      -q, --quiet           suppress program output
      -s, --single          save to a single file
      -t, --text            write files as text (default)
      -v, --version         display current version
      -x [XPATH], --xpath [XPATH]
                            filter HTML using XPath

## Author
* Hunter Hammond (huntrar@gmail.com)

## Notes
* Supports both Python 2.x and Python 3.x.
* You can specify custom output filenames by listing them after --out.
* Pages are saved temporarily as PART.html files during processing. Unless saving pages as HTML, these files are removed automatically upon conversion or exit.
* Images are automatically included when saving as PDF or HTML; this involves making additional HTTP requests, adding a significant amount of processing time. If you wish to forgo this feature use the --no-images flag.
* To crawl pages with no restrictions use the --crawl-all flag, or filter which pages to crawl by URL keywords by passing one or more regexps to --crawl.
* If you want the crawler to follow links outside of the given URL's domain, use --nonstrict.
* Crawling can be stopped by Ctrl-C or alternatively by setting the number of pages or links to be crawled using --maxpages and --maxlinks. A page may contain zero or many links to more pages.
* Filtering HTML can be done using --xpath, while filtering text is done by entering one or more regexps to --filter.
* If you only want to specify specific tag attributes to extract rather than an entire XPath, use --attributes. The default choice is to extract only text attributes, but you can specify one or many different attributes (such as href, src, title, or any attribute available..).
* Multiple files/URL's are saved to multiple output files/directories by default. To consolidate them, use the --single flag.
