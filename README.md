# scrape

## 
a web scraping tool

## Installation
* `pip install scrape`

## Usage
usage: scrape.py [-h] [-f [FILTER [FILTER ...]]] [-c [CRAWL [CRAWL ...]]]
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[-ca]&nbsp;[-l&nbsp;LIMIT]&nbsp;[-t]&nbsp;[-vb]&nbsp;[-v]
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[urls&nbsp;[urls&nbsp;...]]

a web scraping tool

positional arguments:
&nbsp;&nbsp;urls&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;urls&nbsp;to&nbsp;scrape

optional arguments:
&nbsp;&nbsp;-h,&nbsp;--help&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;show&nbsp;this&nbsp;help&nbsp;message&nbsp;and&nbsp;exit
&nbsp;&nbsp;-f&nbsp;[FILTER&nbsp;[FILTER&nbsp;...]],&nbsp;--filter&nbsp;[FILTER&nbsp;[FILTER&nbsp;...]]
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;filter&nbsp;lines&nbsp;by&nbsp;keywords,&nbsp;text&nbsp;only
&nbsp;&nbsp;-c&nbsp;[CRAWL&nbsp;[CRAWL&nbsp;...]],&nbsp;--crawl&nbsp;[CRAWL&nbsp;[CRAWL&nbsp;...]]
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;enter&nbsp;keywords&nbsp;to&nbsp;crawl&nbsp;links
&nbsp;&nbsp;-ca,&nbsp;--crawl-all&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;crawl&nbsp;all&nbsp;links
&nbsp;&nbsp;-l&nbsp;LIMIT,&nbsp;--limit&nbsp;LIMIT
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;crawl&nbsp;page&nbsp;limit
&nbsp;&nbsp;-t,&nbsp;--text&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;write&nbsp;to&nbsp;text&nbsp;instead&nbsp;of&nbsp;pdf
&nbsp;&nbsp;-vb,&nbsp;--verbose&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;show&nbsp;pdfkit&nbsp;errors
&nbsp;&nbsp;-v,&nbsp;--version&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;display&nbsp;current&nbsp;version

## Author
* Hunter Hammond (huntrar@gmail.com)

## Notes
* Unless specified using the --text flag, all webpages are saved as pdf files using pdfkit.

* The --filter flag may be used in conjunction with --text to only save lines matching one or more keywords provided

* Subsequent links may be followed by entering --crawl-all or --crawl. --crawl accepts a list of substrings to control which URL's to crawl.

* There is no limit to the number of pages to be crawled unless one is set using the --limit flag.

