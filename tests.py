#! /usr/bin/env python
import unittest
#import os.path

import prodigal
import translate

class ProdigalTestCase(unittest.TestCase):

    def test_render(self):
        content = "Hello World!"
        self.assertEqual(content, prodigal.render(content))

        content = "{% for i in range(10) %}{{ i }}{% endfor %}"
        self.assertEqual("0123456789", prodigal.render(content))

        content = "{% trans %}Pouac{% endtrans %}"
        self.assertEqual("Pouac", prodigal.render(content))

    def test_translate(self):
        translator = translate.Translator()
        translator.add("{% trans %}Hello world!{% endtrans %}")
        po_content = translator.get_po()
        self.assertEqual("""msgid "Hello world!"
msgstr ""

""", po_content)

if __name__ == "__main__":
    unittest.main()
