# scrape

## a web scraping tool
scrape is a command-line tool for extracting webpages as text or pdf files. The crawling mechanism allows for entire websites to be scraped and also offers regexp support for filtering links and text content. scrape is especially useful for converting online documentation to pdf or just as a faster alternative to wget and grep!

## Installation
* `pip install scrape`
* [Installing wkhtmltopdf](https://github.com/pdfkit/pdfkit/wiki/Installing-WKHTMLTOPDF)

## Usage
    usage: scrape.py [-h] [-c [CRAWL [CRAWL ...]]] [-ca]
                     [-f [FILTER [FILTER ...]]] [-l LIMIT] [-p] [-s] [-v] [-vb]
                     [urls [urls ...]]
    
    a web scraping tool
    
    positional arguments:
      urls                  urls to scrape
    
    optional arguments:
      -h, --help            show this help message and exit
      -c [CRAWL [CRAWL ...]], --crawl [CRAWL [CRAWL ...]]
                            url keywords to crawl links by
      -ca, --crawl-all      crawl all links
      -f [FILTER [FILTER ...]], --filter [FILTER [FILTER ...]]
                            filter lines of text by keywords
      -l LIMIT, --limit LIMIT
                            set crawl page limit
      -p, --pdf             write to pdf instead of text
      -r, --restrict        restrict domain to that of the seed url
      -v, --version         display current version
      -vb, --verbose        print pdfkit log messages

## Author
* Hunter Hammond (huntrar@gmail.com)

## Notes
* --pdf can be used to save web pages as pdf's, they are saved to text by default.

* Text can be filtered by passing one or more regexps to --filter.

* To crawl subsequent pages, enter --crawl followed by one or more regexps which match part of the url. Or instead enter --crawl-all to follow all links.

* To restrict the domain to the seed url's domain, use --strict, otherwise any domain may be followed.

* There is no limit to the number of pages to be crawled unless one is set with --limit, thus to cancel crawling and begin processing simply press Ctrl-C.

