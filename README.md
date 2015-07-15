# scrape

## a web scraping tool
scrape is a command-line tool for extracting webpages as text or pdf files. The crawling mechanism allows for entire websites to be scraped and also offers regexp support for filtering links and text content. scrape is especially useful for converting online documentation to pdf or just as a faster alternative to wget and grep!

## Installation
* `pip install scrape`
* [Installing wkhtmltopdf](https://github.com/pdfkit/pdfkit/wiki/Installing-WKHTMLTOPDF)

## Usage
    usage: scrape.py [-h] [-c [CRAWL [CRAWL ...]]] [-ca]
                     [-f [FILTER [FILTER ...]]] [-fl] [-l LIMIT] [-p] [-s] [-v]
                     [-vb]
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
      -fl, --files          keep .html files instead of writing to text
      -l LIMIT, --limit LIMIT
                            set crawl page limit
      -p, --pdf             write to pdf instead of text
      -s, --strict          restrict crawling to domain of seed url
      -v, --version         display current version
      -vb, --verbose        print log and error messages

## Author
* Hunter Hammond (huntrar@gmail.com)

## Notes
* Conversion to text occurs by default, use --pdf or --files to save to pdf or .html files, respectively.

* Text can be filtered by passing one or more regexps to --filter.

* Pages are saved temporarily as PART.html files and removed after they are written to pdf or text. Using --files not only preserves these files but also creates subdirectories for them, named after their seed domain.

* To crawl subsequent pages, enter --crawl followed by one or more regexps which match part of the url. To crawl all links regardless of the url, use --crawl-all.

* To restrict the domain to the seed url's domain, use --strict, otherwise any domain may be followed.

* There is no limit to the number of pages to be crawled unless one is set with --limit, thus to cancel crawling and begin processing simply press Ctrl-C.

