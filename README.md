# scrape

## a command-line web scraping tool
scrape is a command-line tool for extracting webpages as text or pdf files. The crawling mechanism allows for entire websites to be scraped and also offers regexp support for filtering links and text content. scrape is especially useful for converting online documentation to pdf or just as a faster alternative to wget and grep!

## Installation
* `pip install scrape`
* [Installing wkhtmltopdf](https://github.com/pdfkit/pdfkit/wiki/Installing-WKHTMLTOPDF)

## Usage
    usage: scrape.py [-h] [-a [ATTRIBUTES [ATTRIBUTES ...]]]
                     [-c [CRAWL [CRAWL ...]]] [-ca] [-f [FILTER [FILTER ...]]]
                     [-ht] [-l LIMIT] [-p] [-q] [-s] [-t] [-v]
                     [urls [urls ...]]
    
    a web scraping tool
    
    positional arguments:
      urls                  url(s) to scrape
    
    optional arguments:
      -h, --help            show this help message and exit
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
      -p, --pdf             save output as pdf
      -q, --quiet           suppress output
      -s, --strict          set crawler to not visit other websites
      -t, --text            save output as text, default
      -v, --version         display current version

## Author
* Hunter Hammond (huntrar@gmail.com)

## Notes
* Pages are converted to text by default, you can specify --html or --pdf to save to a different format.

* If saving to text, lines may be filtered for keywords by passing one or more regexps to --filter.

* Also if saving to text, you may specify specific tag attributes to extract from the page using --attributes. The default choice is to extract only text attributes, but you can specify one or many different attributes (such as href, src, title, or any attribute available..).

* Pages are saved temporarily as PART%d.html files during processing. These files are removed automatically if saving to text or pdf.

* Entire websites can be downloaded by using the --crawl-all flag or by passing one or more regexps to --crawl, which filters through a list of URL's.

* If you do not want the crawler to follow links outside of the given website, use --strict.

* Crawling can be stopped by Ctrl-C or by setting the number of pages to be crawled using --limit.

