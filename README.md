# scrape

## a web scraping tool
scrape is a command-line tool for extracting webpages as text or pdf files. The crawling mechanism allows for entire websites to be scraped and also offers regexp support for filtering links and text content. scrape is especially useful for converting online documentation to pdf or just as a faster alternative to wget and grep!

## Installation
* `pip install scrape`
* [Installing wkhtmltopdf](https://github.com/pdfkit/pdfkit/wiki/Installing-WKHTMLTOPDF)

## Usage
    usage: scrape [-h] [-c [CRAWL [CRAWL ...]]] [-ca] [-f [FILTER [FILTER ...]]]
                  [-ht] [-l LIMIT] [-p] [-q] [-s] [-t] [-v]
                  [urls [urls ...]]
    
    a web scraping tool
    
    positional arguments:
      urls                  url(s) to scrape
    
    optional arguments:
      -h, --help            show this help message and exit
      -c [CRAWL [CRAWL ...]], --crawl [CRAWL [CRAWL ...]]
                            regexp(s) to match links to crawl
      -ca, --crawl-all      crawl all links
      -f [FILTER [FILTER ...]], --filter [FILTER [FILTER ...]]
                            regexp(s) to filter lines of text
      -ht, --html           save output as html
      -l LIMIT, --limit LIMIT
                            set page crawling limit
      -p, --pdf             save output as pdf
      -q, --quiet           suppress output
      -s, --strict          set crawler to not visit other websites
      -t, --text            save output as text, default
      -v, --version         display current version

## Author
* Hunter Hammond (huntrar@gmail.com)

## Notes
* Text can be filtered line by line by passing one or more regexps to --filter.

* Pages are saved temporarily as PART%d.html files during processing. These files are removed automatically if saving to text or pdf.

* Entire websites can be downloaded by using the --crawl-all flag or by passing one or more regexps to --crawl, which filters through a list of URL's.

* If you do not want the crawler to follow links outside of the given website, use --strict.

* Crawling can be stopped by Ctrl-C or by setting the number of pages to be crawled using --limit.

