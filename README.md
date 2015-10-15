# scrape [![Build Status](https://travis-ci.org/huntrar/scrape.svg?branch=master)](https://travis-ci.org/huntrar/scrape) [![PyPI](https://img.shields.io/pypi/dm/scrape.svg?style=flat)]()

## a command-line web scraping tool

scrape can extract, filter, and convert webpages to text, pdf, or HTML files. A link crawler can traverse websites using regular expression keywords. Users may also choose to enter local files to filter and/or convert.

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
    usage: scrape.py [-h] [-l [LOCAL [LOCAL ...]]]
                     [-a [ATTRIBUTES [ATTRIBUTES ...]]] [-c [CRAWL [CRAWL ...]]]
                     [-ca] [-f [FILTER [FILTER ...]]] [-ht] [-mp MAXPAGES]
                     [-ml MAXLINKS] [-n] [-p] [-q] [-t] [-v]
                     [urls [urls ...]]
    
    a command-line web scraping tool
    
    positional arguments:
      urls                  urls to scrape
    
    optional arguments:
      -h, --help            show this help message and exit
      -l [LOCAL [LOCAL ...]], --local [LOCAL [LOCAL ...]]
                            read in HTML files
      -a [ATTRIBUTES [ATTRIBUTES ...]], --attributes [ATTRIBUTES [ATTRIBUTES ...]]
                            extract text using tag attributes
      -c [CRAWL [CRAWL ...]], --crawl [CRAWL [CRAWL ...]]
                            regexp rules for following new pages
      -ca, --crawl-all      crawl all pages
      -f [FILTER [FILTER ...]], --filter [FILTER [FILTER ...]]
                            regexp rules for filtering text
      -ht, --html           write pages as HTML
      -mp MAXPAGES, --maxpages MAXPAGES
                            max number of pages to crawl
      -ml MAXLINKS, --maxlinks MAXLINKS
                            max number of links to scrape
      -n, --nonstrict       allow crawler to visit any domain
      -p, --pdf             write pages as pdf
      -q, --quiet           suppress program output
      -t, --text            write pages as text (default)
      -v, --version         display current version

## Author
* Hunter Hammond (huntrar@gmail.com)

## Notes
* Supports both Python 2.x and Python 3.x.
* Pages are converted to text by default, you can specify --html or --pdf to save to a different format.
* Use the --local flag to read in local HTML files instead of entering a URL.
* Filtering text is done by entering one or more regexps to --filter.
* You may specify specific tag attributes to extract from the page using --attributes. The default choice is to extract only text attributes, but you can specify one or many different attributes (such as href, src, title, or any attribute available..).
* Pages are saved temporarily as PART.html files during processing. Unless saving pages as HTML, these files are removed automatically upon conversion or exit.
* To crawl pages with no restrictions use the --crawl-all flag, or filter which pages to crawl by URL keywords by passing one or more regexps to --crawl.
* If you want the crawler to follow links outside of the given URL's domain, use --nonstrict.
* Crawling can be stopped by Ctrl-C or alternatively by setting the number of pages or links to be crawled using --maxpages and --maxlinks. A page may contain zero or many links to more pages.
