#!/usr/bin/env python

''' Unit tests for scrape '''

import glob
import shutil
import unittest
import os

from scrape import scrape, utils



class ScrapeTestCase(unittest.TestCase):
    
    def call_scrape(self, cmd, file_type): 
        parser = scrape.get_parser()
        args = vars(parser.parse_args(cmd))
        args[file_type] = True
        return scrape.scrape(args)

    def setUp(self):
        self.html_files = list(glob.glob('*.html'))
        self.url = 'http://github.com/huntrar/scrape'

    def tearDown(self):
        pass

    def test_html_to_text(self):
        self.call_scrape(self.html_files, 'text')
        out_file_names = [x.replace('.html', '.txt') for x in self.html_files]
        
        ''' Assert new files have been created, then assert their deletion '''
        for out_file in out_file_names:
            self.assertTrue(os.path.isfile(out_file))
            self.assertTrue(utils.remove_file(out_file))

    ''' Requires whtmltopdf executable to run
    def test_html_to_pdf(self):
        self.call_scrape(self.html_files, 'pdf')
        out_file_names = [x.replace('.html', '.pdf') for x in self.html_files]
        
        # Assert new files have been created, then assert their deletion
        for out_file in out_file_names:
            self.assertTrue(os.path.isfile(out_file))
            self.assertTrue(utils.remove_file(out_file))
    '''

    ''' Requires whtmltopdf executable to run
    def test_url_to_pdf(self):
        self.call_scrape([self.url], 'pdf')
        out_file = utils.get_out_filename(self.url) + '.pdf'
        self.assertTrue(os.path.isfile(out_file)) 
        self.assertTrue(utils.remove_file(out_file))
    '''

    def test_url_to_text(self):
        self.call_scrape([self.url], 'text')
        out_file = utils.get_out_filename(self.url) + '.txt'
        self.assertTrue(os.path.isfile(out_file)) 
        self.assertTrue(utils.remove_file(out_file))

    def test_url_to_html(self):
        self.call_scrape([self.url], 'html')
        domain = utils.get_domain(self.url)
        self.assertTrue(os.path.isfile('{0}/PART1.html'.format(domain)))

        ''' Delete subdirectory containing HTML files if no other data in it '''
        subdir_path = '{0}/{1}'.format(os.getcwd(), domain)
        files = os.listdir(subdir_path)
        files_to_rm = [x for x in files if 'PART' in x]

        if len(files_to_rm) != len(files):
            for file_name in files_to_rm:
                os.remove(file_name)
        else:
            shutil.rmtree(subdir_path)
        

if __name__ == '__main__':
    unittest.main()
