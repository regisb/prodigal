#! /usr/bin/env python
import unittest
#import os.path

import prodigal

class ProdigalTestCase(unittest.TestCase):
    #def test_find_files(self):
        ## Find all files in current directory
        #path  = os.path.dirname(os.path.abspath(__file__))
        #files = prodigal.find_files(path)
        #self.assertLessEqual(1, len(files))
        #self.assertIn(os.path.join(path, "tests.py"), files)

    def test_render(self):
        content = "Hello World!"
        self.assertEqual(content, prodigal.render(content))

        content = "{% for i in range(10) %}{{ i }}{% endfor %}"
        self.assertEqual("0123456789", prodigal.render(content))

        content = "{% trans %}Pouac{% endtrans %}"
        self.assertEqual("Pouac", prodigal.render(content))

if __name__ == "__main__":
    unittest.main()
