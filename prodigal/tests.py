#! /usr/bin/env python
import unittest
import tempfile
import os

import tools
import translate

class ProdigalTestCase(unittest.TestCase):

    def test_render(self):
        content = "Hello World!"
        self.assertEqual(content, tools.render(content))

        content = "{% for i in range(10) %}{{ i }}{% endfor %}"
        self.assertEqual("0123456789", tools.render(content))

        content = "{% trans %}Pouac{% endtrans %}"
        self.assertEqual("Pouac", tools.render(content))

    def test_translate(self):
        translator = translate.Translator()
        translator.add("{% trans %}Hello world!{% endtrans %}")
        po_content = translator.get_po()
        self.assertEqual("""msgid "Hello world!"
msgstr ""

""", po_content)

    def test_translate_file(self):
        tmp = tempfile.NamedTemporaryFile()
        tmp.write("{% trans %}Pouac{% endtrans %}")
        tmp.flush()

        translator = translate.Translator()
        translator.add_file(tmp.name)
        po_content = translator.get_po()
        self.assertEqual("""#: %s:1
msgid "Pouac"
msgstr ""

""" % tmp.name, po_content)

    def test_compile(self):
        po_path = "/tmp/fr.po"
        mo_path = "/tmp/fr.mo"
        with open(po_path, "w") as tmp:
            tmp.write("""#: /some/file:1
msgid "Hello world!"
msgstr "Bonjour tout le monde !"
""")
        if os.path.exists(mo_path):
            os.remove(mo_path)

        translate.compile(po_path)
        self.assertTrue(os.path.exists(mo_path))
        os.remove(mo_path)
        os.remove(po_path)

if __name__ == "__main__":
    unittest.main()
