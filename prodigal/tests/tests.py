#! /usr/bin/env python
import unittest
import tempfile
import os
import shutil

from prodigal import tools
from prodigal import translate
from prodigal import templates

class ProdigalTestCase(unittest.TestCase):

    def test_should_render(self):
        self.assertTrue(templates.should_render("index.html"))
        self.assertFalse(templates.should_render("_base.html"))
        self.assertFalse(templates.should_render("/tmp/_base.html"))
        self.assertFalse(templates.should_render("/tmp/.gitignore"))
        self.assertFalse(templates.should_render(".index.html.swp"))

    def test_list_templates(self):
        root = tempfile.mkdtemp()
        f1 = tempfile.NamedTemporaryFile(suffix=".htm", dir=root, delete=False)
        f2 = tempfile.NamedTemporaryFile(suffix=".html", dir=root, delete=False)

        template_list = list(templates.list(root))
        template_set = set(template_list)
        self.assertEqual(2, len(template_list))
        self.assertIn(f1.name, template_set)
        self.assertIn(f2.name, template_set)

        shutil.rmtree(root)

    def test_render(self):
        content = "Hello World!"
        self.assertEqual(content, tools.render(content))

        content = "{% for i in range(10) %}{{ i }}{% endfor %}"
        self.assertEqual("0123456789", tools.render(content))

        content = "{% trans %}Pouac{% endtrans %}"
        self.assertEqual("Pouac", tools.render(content))

    def test_should_translate(self):
        self.assertTrue(templates.should_translate("index.html"))
        self.assertTrue(templates.should_translate("/tmp/_base.html"))
        self.assertFalse(templates.should_translate("/tmp/.gitignore"))
        self.assertFalse(templates.should_translate(".index.html.swp"))

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

    def test_translation_updater(self):
        src_path = tempfile.mkdtemp()
        updater = translate.Updater(src_path, "fr")
        po_path = os.path.join(src_path, "fr.po")
        mo_path = os.path.join(src_path, "fr.mo")

        # .po file doesn't exist
        self.assertFalse(updater.run())

        # Create po file
        with open(po_path, "w"):
            pass

        # .mo file doesn't exist
        self.assertTrue(updater.run())
        self.assertTrue(os.path.exists(mo_path))

        # .mo file was compiled just now
        self.assertFalse(updater.run())

        shutil.rmtree(src_path)

class ToolsTranslateTest(unittest.TestCase):
    def setUp(self):
        self.src_path = tempfile.mkdtemp()
        self.dst_path = tempfile.mkdtemp()
        self.f1 = tempfile.NamedTemporaryFile(suffix=".html", dir=self.src_path, delete=False)
        self.f2 = tempfile.NamedTemporaryFile(suffix=".htm", dir=self.src_path, delete=False)
        self.f1.write("{% trans %}Hello World!{% endtrans %}")
        self.f1.flush()

    def test_translate(self):
        po_path = os.path.join(self.src_path, "fr.po")

        # Translate once
        tools.translate_templates("fr", self.src_path)

        self.assertTrue(os.path.exists(po_path))
        translations = """#: %s:1
msgid "Hello World!"
msgstr ""

""" % self.f1.name
        self.assertEqual(translations, open(po_path).read())

        # Modify translations
        translations = """#: %s:1
msgid "Hello World!"
msgstr "Bonjour tout le monde !"

""" % self.f1.name
        with open(po_path, "w") as f:
            f.write(translations)

        # Translate twice
        tools.translate_templates("fr", self.src_path)
        self.assertEqual(translations, open(po_path).read())

    def tearDown(self):
        shutil.rmtree(self.src_path)
        shutil.rmtree(self.dst_path)

class ToolsGenerateTest(unittest.TestCase):
    def setUp(self):
        self.src_path = tempfile.mkdtemp()
        self.dst_path = tempfile.mkdtemp()
        self.f1 = tempfile.NamedTemporaryFile(suffix=".html", dir=self.src_path, delete=False)
        self.f2 = tempfile.NamedTemporaryFile(suffix=".htm", dir=self.src_path, delete=False)
        self.f1.write("{% trans %}Hello World!{% endtrans %}")
        self.f1.flush()

    def tearDown(self):
        shutil.rmtree(self.src_path)
        shutil.rmtree(self.dst_path)

    def test_without_locale(self):
        tools.generate(self.src_path, self.dst_path)

        f1_dst_path = os.path.join(self.dst_path, os.path.basename(self.f1.name))
        f2_dst_path = os.path.join(self.dst_path, os.path.basename(self.f2.name))
        self.assertTrue(os.path.exists(f1_dst_path))
        self.assertFalse(os.path.exists(f2_dst_path))
        self.assertEqual("Hello World!", open(f1_dst_path).read())

    def test_with_locale(self):
        po_path = os.path.join(self.src_path, "fr.po")
        mo_path = os.path.join(self.src_path, "fr.mo")
        with open(po_path, "w") as tmp:
            tmp.write("""msgid "Hello World!"
msgstr "Bonjour tout le monde !"
""")
        tools.generate(self.src_path, self.dst_path, "fr")

        self.assertTrue(os.path.exists(mo_path))
        f1_dst_path = os.path.join(self.dst_path, os.path.basename(self.f1.name))
        f2_dst_path = os.path.join(self.dst_path, os.path.basename(self.f2.name))
        self.assertTrue(os.path.exists(f1_dst_path))
        self.assertFalse(os.path.exists(f2_dst_path))
        self.assertEqual("Bonjour tout le monde !", open(f1_dst_path).read())

def main():
    unittest.main()

if __name__ == "__main__":
    main()
