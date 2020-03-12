#!/usr/bin/env python

"""Unit tests for scrape"""

import os
import shutil
import sys
import unittest

from scrape import scrape, utils


class ScrapeTestCase(unittest.TestCase):
    def call_scrape(self, cmd, filetype, num_files=None):
        if not isinstance(cmd, list):
            cmd = [cmd]
        parser = scrape.get_parser()
        args = vars(parser.parse_args(cmd))

        args["overwrite"] = True  # Avoid overwrite prompt
        if args["crawl"] or args["crawl_all"]:
            args["no_images"] = True  # Avoid save image prompt when crawling
        args[filetype] = True
        if num_files is not None:
            args[num_files] = True
        return scrape.scrape(args)

    def setUp(self):
        self.original_files = os.listdir(os.getcwd())
        self.html_files = [x for x in self.original_files if x.endswith(".html")]
        self.text_files = [x for x in self.original_files if x.endswith(".txt")]
        self.query = self.html_files + self.text_files

    def tearDown(self):
        pass

    def assert_exists_and_rm(self, filename):
        self.assertTrue(os.path.isfile(filename))
        if filename not in self.original_files:
            self.assertTrue(utils.remove_file(filename))

    def delete_subdir(self, domain):
        """Delete subdirectory containing HTML files if no other data in it"""
        subdir_path = "{0}/{1}".format(os.getcwd(), domain)
        files = os.listdir(subdir_path)
        files_to_rm = [x for x in files if x.startswith("PART") and x.endswith(".html")]

        if len(files_to_rm) != len(files):
            for filename in files_to_rm:
                os.remove(filename)
        else:
            shutil.rmtree(subdir_path)

    def get_single_outfilename(self, query):
        """Use first possible entry in query as filename"""
        if not isinstance(query, list):
            query = [query]
        for arg in query:
            if arg in self.html_files or arg in self.text_files:
                return (".".join(arg.split(".")[:-1])).lower()
        sys.stderr.write("Failed to construct a single out filename.\n")
        return ""

    """to_pdf functions require wkhtmltopdf executable to run
    def test_query_to_multi_pdf(self):
        self.call_scrape(self.query, 'pdf', 'multiple')
        for filename in self.html_files + self.text_files:
            outfilename = '.'.join(filename.split('.')[:-1]) + '.pdf'
            self.assert_exists_and_rm(outfilename)

    def test_query_to_single_pdf(self):
        self.call_scrape(self.query, 'pdf', 'single')
        outfilename = self.get_single_outfilename(self.query) + '.pdf'
        self.assert_exists_and_rm(outfilename)

    def test_html_to_pdf(self):
        self.call_scrape(self.html_files, 'pdf')
        outfilenames = [x.replace('.html', '.pdf') for x in self.html_files]

        # Assert new files have been created, then assert their deletion
        for outfilename in outfilenames:
            self.assert_exists_and_rm(outfilename)

    def test_text_to_pdf(self):
        self.call_scrape(self.text_files, 'pdf')
        outfilenames = [x.replace('.txt', '.pdf') for x in self.text_files]

        # Assert new files have been created, then assert their deletion
        for outfilename in outfilenames:
            self.assert_exists_and_rm(outfilename)
   """

    def test_query_to_multi_text(self):
        self.call_scrape(self.query, "text", "multiple")
        for filename in self.html_files + self.text_files:
            outfilename = ".".join(filename.split(".")[:-1]) + ".txt"
            self.assert_exists_and_rm(outfilename)

    def test_query_to_single_text(self):
        self.call_scrape(self.query, "text", "single")
        outfilename = self.get_single_outfilename(self.query) + ".txt"
        self.assert_exists_and_rm(outfilename)

    def test_html_to_text(self):
        self.call_scrape(self.html_files, "text")
        outfilenames = [x.replace(".html", ".txt") for x in self.html_files]

        # Assert new files have been created, then assert their deletion
        for outfilename in outfilenames:
            self.assert_exists_and_rm(outfilename)


if __name__ == "__main__":
    unittest.main()
