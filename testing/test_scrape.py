#!/usr/bin/env python

''' Unit tests for scrape '''

import shutil
import unittest
import os

from scrape import scrape, utils



class ScrapeTestCase(unittest.TestCase):
    
    def call_scrape(self, cmd, file_type, num_files=False): 
        parser = scrape.get_parser()
        args = vars(parser.parse_args(cmd))
        args[file_type] = True
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

    def assert_exists_and_rm(self, file_name):
        self.assertTrue(os.path.isfile(file_name))
        if file_name not in self.original_files:
            self.assertTrue(utils.remove_file(file_name))

    def delete_subdir(self, domain):
        ''' Delete subdirectory containing HTML files if no other data in it '''
        subdir_path = '{0}/{1}'.format(os.getcwd(), domain)
        files = os.listdir(subdir_path)
        files_to_rm = [x for x in files if x.startswith('PART')
                       and x.endswith('.html')]

        if len(files_to_rm) != len(files):
            for file_name in files_to_rm:
                os.remove(file_name)
        else:
            shutil.rmtree(subdir_path)

    def get_single_out_name(self):
        out_file_name = ''
        possible_out_name = ''
        out_it = 0
        ''' Use first possible entry in query as filename '''
        try:
            while not out_file_name:
                possible_out_name = self.query[out_it]
                if (possible_out_name in self.html_files or
                    possible_out_name in self.text_files):
                    return '.'.join(possible_out_name.split('.')[:-1])
                for url in self.urls:
                    if possible_out_name in url:
                        domain = utils.get_domain(url)
                        return utils.get_out_filename(url, domain)
                        break
                out_it += 1
        except IndexError:
            sys.stderr.write('Failed to choose an out file name\n')
            raise
        return ''

    ''' to_pdf functions require wkhtmltopdf executable to run
    def test_query_to_multi_pdf(self):
        self.call_scrape(self.query, 'pdf', 'multiple')
        for file_name in self.html_files + self.text_files:
            out_file_name = '.'.join(file_name.split('.')[:-1]) + '.pdf'
            self.assert_exists_and_rm(out_file_name)

        for url in self.urls:
            domain = utils.get_domain(url)
            out_file_name = utils.get_out_filename(url, domain) + '.pdf'
            self.assert_exists_and_rm(out_file_name)

    def test_query_to_single_pdf(self):
        self.call_scrape(self.query, 'pdf', 'single')
        out_file_name = self.get_single_out_name() + '.pdf'
        self.assert_exists_and_rm(out_file_name)

    def test_html_to_pdf(self):
        self.call_scrape(self.html_files, 'pdf')
        out_file_names = [x.replace('.html', '.pdf') for x in self.html_files]
        
        # Assert new files have been created, then assert their deletion
        for out_file_name in out_file_names:
            self.assert_exists_and_rm(out_file_name)

    def test_urls_to_pdf(self):
        self.call_scrape(self.urls, 'pdf')
        for url in self.urls:
            out_file_name = utils.get_out_filename(url) + '.pdf'
            self.assert_exists_and_rm(out_file_name)

    def test_text_to_pdf(self):
        self.call_scrape(self.text_files, 'pdf')
        out_file_names = [x.replace('.txt', '.pdf') for x in self.text_files]

        # Assert new files have been created, then assert their deletion
        for out_file_name in out_file_names:
            self.assert_exists_and_rm(out_file_name)
    '''

    def test_query_to_multi_text(self):
        self.call_scrape(self.query, 'text', 'multiple')
        for file_name in self.html_files + self.text_files:
            out_file_name = '.'.join(file_name.split('.')[:-1]) + '.txt'
            self.assert_exists_and_rm(out_file_name)

        for url in self.urls:
            domain = utils.get_domain(url)
            out_file_name = utils.get_out_filename(url, domain) + '.txt'
            self.assert_exists_and_rm(out_file_name)
    
    def test_query_to_single_text(self):
        self.call_scrape(self.query, 'text', 'single')
        out_file_name = self.get_single_out_name() + '.txt'
        self.assert_exists_and_rm(out_file_name)

    def test_urls_to_text(self):
        self.call_scrape(self.urls, 'text')
        for url in self.urls:
            out_file_name = utils.get_out_filename(url) + '.txt'
            self.assert_exists_and_rm(out_file_name)

    def test_html_to_text(self):
        self.call_scrape(self.html_files, 'text')
        out_file_names = [x.replace('.html', '.txt') for x in self.html_files]
        
        ''' Assert new files have been created, then assert their deletion '''
        for out_file_name in out_file_names:
            self.assert_exists_and_rm(out_file_name)

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
