# scrape

## 
a webpage scraping tool

## Installation
* `pip install scrape`

## Usage
usage: scrape.py [-h] [-c [CRAWL [CRAWL ...]]] [-ca] [-l LIMIT] [-t]
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;url [keywords [keywords ...]]

a webpage scraping tool

&nbsp;&nbsp;positional arguments:

&nbsp;&nbsp;&nbsp;&nbsp;url&nbsp;&nbsp;&nbsp;url to scrape

&nbsp;&nbsp;&nbsp;&nbsp;keywords&nbsp;&nbsp;&nbsp;keywords to search


&nbsp;&nbsp;optional arguments:

&nbsp;&nbsp;&nbsp;&nbsp;-h, --help&nbsp;&nbsp;show this help message and exit

&nbsp;&nbsp;&nbsp;&nbsp;-c [CRAWL [CRAWL ...]], --crawl [CRAWL [CRAWL ...]]
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;crawl links based on these keywords

&nbsp;&nbsp;&nbsp;&nbsp;-ca, --crawl-all&nbsp;&nbsp;crawl all links

&nbsp;&nbsp;-l LIMIT, --limit LIMIT&nbsp;&nbsp;&nbsp;&nbsp;crawl page limit

&nbsp;&nbsp;-t, --text&nbsp;&nbsp;&nbsp;&nbsp;write to text instead of pdf


## Author
* Hunter Hammond (huntrar@gmail.com)

## Notes
* Unless specified using the --text flag, all webpages are saved as pdf files using pdfkit.

* Entering keyword arguments while using the --text flag allows users to save only lines matching one of the given keywords.

* You can crawl subsequent webpages using by passing a substring of the url you wish to match using --crawl, or by using --crawl-all.

* There is no limit to the number of pages to be crawled unless one is set using the --limit flag.

