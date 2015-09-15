# scrape

## a command-line web scraping and crawling tool
[![Build Status](https://travis-ci.org/huntrar/scrape.svg?branch=master)](https://travis-ci.org/huntrar/scrape)

scrape is a command-line tool used to quickly extract and filter webpages in a grep-like manner. It allows saving in the form of text, pdf, or HTML. Users may provide their own HTML files to convert or filter. A crawling mechanism allows scrape to traverse websites by regex keywords or can also be run freely. scrape can extract data from any DOM tags, an example being entering 'href' for all links or 'text' for all plaintext.

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
    usage: scrape.py [-h] [-r [READ [READ ...]]]
                     [-a [ATTRIBUTES [ATTRIBUTES ...]]] [-c [CRAWL [CRAWL ...]]]
                     [-ca] [-f [FILTER [FILTER ...]]] [-ht] [-l LIMIT] [-n] [-p]
                     [-q] [-t] [-v]
                     [urls [urls ...]]
    
    a command-line web scraping and crawling tool
    
    positional arguments:
      urls                  url(s) to scrape
    
    optional arguments:
      -h, --help            show this help message and exit
      -r [READ [READ ...]], --read [READ [READ ...]]
                            read in local html file(s)
      -a [ATTRIBUTES [ATTRIBUTES ...]], --attributes [ATTRIBUTES [ATTRIBUTES ...]]
                            tag attribute(s) for extracting lines of text, default
                            is text
      -c [CRAWL [CRAWL ...]], --crawl [CRAWL [CRAWL ...]]
                            regexp(s) to match links to crawl
      -ca, --crawl-all      crawl all links
      -f [FILTER [FILTER ...]], --filter [FILTER [FILTER ...]]
                            regexp(s) to filter lines of text
      -ht, --html           save output as html
      -l LIMIT, --limit LIMIT
                            set page crawling limit
      -n, --nonstrict       set crawler to visit other websites
      -p, --pdf             save output as pdf
      -q, --quiet           suppress output
      -t, --text            save output as text, default
      -v, --version         display current version

## Author
* Hunter Hammond (huntrar@gmail.com)

## Notes
* Supports both Python 2.x and Python 3.x.
* Pages are converted to text by default, you can specify --html or --pdf to save to a different format.
* Use the --read flag to read in local HTML files and extract, filter, or convert their contents.
* Filtering text is done by entering one or more regexps to --filter.
* You may specify specific tag attributes to extract from the page using --attributes. The default choice is to extract only text attributes, but you can specify one or many different attributes (such as href, src, title, or any attribute available..).
* Pages are saved temporarily as PART(%d).html files during processing and are removed automatically upon format conversion or unexpected exit.
* Entire websites can be downloaded by using the --crawl-all flag or by passing one or more regexps to --crawl, which filters a list of URL's.
* If you want the crawler to follow links outside of the given URL's domain, use --nonstrict.
* Crawling can be stopped by Ctrl-C or by setting the number of pages to be crawled using --limit.

