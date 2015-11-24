#!/usr/bin/env python

''' Unit tests for scrape '''

import os
import shutil
import unittest

from scrape import scrape, utils



class ScrapeTestCase(unittest.TestCase):
    
    def call_scrape(self, cmd, filetype, num_files=False): 
        parser = scrape.get_parser()
        args = vars(parser.parse_args(cmd))
        args[filetype] = True
        if num_files:
            args[num_files] = True
        return scrape.scrape(args)

    def setUp(self):
        self.original_files = os.listdir(os.getcwd())
        self.html_files = [x for x in self.original_files
                           if x.endswith('.html')]
        self.text_files = [x for x in self.original_files
                           if x.endswith('.txt')]
        self.urls = ['http://github.com/huntrar/scrape',
                     'http://stackoverflow.com']
        self.query = self.html_files + self.text_files + self.urls

    def tearDown(self):
        pass

    def assert_exists_and_rm(self, filename):
        self.assertTrue(os.path.isfile(filename))
        if filename not in self.original_files:
            self.assertTrue(utils.remove_file(filename))

    def delete_subdir(self, domain):
        ''' Delete subdirectory containing HTML files if no other data in it '''
        subdir_path = '{0}/{1}'.format(os.getcwd(), domain)
        files = os.listdir(subdir_path)
        files_to_rm = [x for x in files if x.startswith('PART')
                       and x.endswith('.html')]

        if len(files_to_rm) != len(files):
            for filename in files_to_rm:
                os.remove(filename)
        else:
            shutil.rmtree(subdir_path)

    def get_single_outfilename(self):
        ''' Use first possible entry in query as filename '''
        for arg in self.query:
            if arg in self.html_files or arg in self.text_files:
                return ('.'.join(arg.split('.')[:-1])).lower()
            for url in self.urls:
                if arg.strip('/') in url:
                    domain = utils.get_domain(url)
                    return utils.get_outfilename(url, domain)
        sys.stderr.write('Failed to construct a single out filename.\n')
        return ''

    ''' to_pdf functions require wkhtmltopdf executable to run
    def test_query_to_multi_pdf(self):
        self.call_scrape(self.query, 'pdf', 'multiple')
        for filename in self.html_files + self.text_files:
            outfilename = '.'.join(filename.split('.')[:-1]) + '.pdf'
            self.assert_exists_and_rm(outfilename)

        for url in self.urls:
            domain = utils.get_domain(url)
            outfilename = utils.get_outfilename(url, domain) + '.pdf'
            self.assert_exists_and_rm(outfilename)

    def test_query_to_single_pdf(self):
        self.call_scrape(self.query, 'pdf', 'single')
        outfilename = self.get_single_outfilename() + '.pdf'
        self.assert_exists_and_rm(outfilename)

    def test_html_to_pdf(self):
        self.call_scrape(self.html_files, 'pdf')
        outfilenames = [x.replace('.html', '.pdf') for x in self.html_files]
        
        # Assert new files have been created, then assert their deletion
        for outfilename in outfilenames:
            self.assert_exists_and_rm(outfilename)

    def test_urls_to_pdf(self):
        self.call_scrape(self.urls, 'pdf')
        for url in self.urls:
            outfilename = utils.get_outfilename(url) + '.pdf'
            self.assert_exists_and_rm(outfilename)

    def test_text_to_pdf(self):
        self.call_scrape(self.text_files, 'pdf')
        outfilenames = [x.replace('.txt', '.pdf') for x in self.text_files]

        # Assert new files have been created, then assert their deletion
        for outfilename in outfilenames:
            self.assert_exists_and_rm(outfilename)
    '''

    def test_query_to_multi_text(self):
        self.call_scrape(self.query, 'text', 'multiple')
        for filename in self.html_files + self.text_files:
            outfilename = '.'.join(filename.split('.')[:-1]) + '.txt'
            self.assert_exists_and_rm(outfilename)

        for url in self.urls:
            domain = utils.get_domain(url)
            outfilename = utils.get_outfilename(url, domain) + '.txt'
            self.assert_exists_and_rm(outfilename)
    
    def test_query_to_single_text(self):
        self.call_scrape(self.query, 'text', 'single')
        outfilename = self.get_single_outfilename() + '.txt'
        self.assert_exists_and_rm(outfilename)

    def test_urls_to_text(self):
        self.call_scrape(self.urls, 'text')
        for url in self.urls:
            outfilename = utils.get_outfilename(url) + '.txt'
            self.assert_exists_and_rm(outfilename)

    def test_html_to_text(self):
        self.call_scrape(self.html_files, 'text')
        outfilenames = [x.replace('.html', '.txt') for x in self.html_files]
        
        ''' Assert new files have been created, then assert their deletion '''
        for outfilename in outfilenames:
            self.assert_exists_and_rm(outfilename)

    def test_query_to_multi_html(self):
        self.call_scrape(self.query, 'html', 'multiple')
        for url in self.urls:
            domain = utils.get_domain(url)
            self.assertTrue(os.path.isfile('{0}/PART1.html'.format(domain)))
            self.delete_subdir(domain)

    def test_query_to_single_html(self):
        self.call_scrape(self.query, 'html', 'single')
        domain = utils.get_domain(self.urls[0])
        self.assertTrue(os.path.isfile('{0}/PART1.html'.format(domain)))
        self.delete_subdir(domain)

    def test_urls_to_html(self):
        self.call_scrape(self.urls, 'html')
        for url in self.urls:
            domain = utils.get_domain(url)
            self.assertTrue(os.path.isfile('{0}/PART1.html'.format(domain)))
            self.delete_subdir(domain)


if __name__ == '__main__':
    unittest.main()
