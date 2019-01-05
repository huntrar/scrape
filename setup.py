#!/usr/bin/env python

from setuptools import setup, find_packages
import scrape
import os

def read(*names):
    values = dict()
    extensions = ['.txt', '.rst']
    for name in names:
        value = ''
        for extension in extensions:
            filename = name + extension
            if os.path.isfile(filename):
                value = open(name + extension).read()
                break
        values[name] = value
    return values

long_description = """
%(README)s

News
====

%(CHANGES)s

""" % read('README', 'CHANGES')

setup(
    name='scrape',
    version=scrape.__version__,
    description='a command-line web scraping tool',
    long_description=long_description,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Utilities",
        "Topic :: Text Processing",
    ],
    keywords='web crawler scraper scrape crawl download filter save webpages websites images docs document documentation pdf csv html lxml',
    author='Hunter Hammond',
    author_email='huntrar@gmail.com',
    maintainer='Hunter Hammond',
    maintainer_email='huntrar@gmail.com',
    url='https://github.com/huntrar/scrape',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'scrape = scrape.scrape:command_line_runner',
        ]
    },
    install_requires=[
        'lxml',
        'pdfkit',
        'requests',
        'six',
        'tldextract',
    ]
)
