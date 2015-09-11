#!/usr/bin/env python

from setuptools import setup, find_packages
import scrape
import os

def read(*names):
    values = dict()
    extensions = ['.txt', '.md']
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
    description='a command-line web scraping and crawling tool',
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='scrape entire webpage website pdf text keyword crawl save page filter regex lxml html download downloader',
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
        'requests'
    ]
)
