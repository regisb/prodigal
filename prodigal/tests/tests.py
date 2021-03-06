#! /usr/bin/env python
import unittest
import tempfile
import os
import shutil

from prodigal import jinjaenv
from prodigal import tools
from prodigal import translate
from prodigal import templates
from prodigal import filters

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

        template_list = list(templates.list_files(root))
        template_set = set(template_list)
        self.assertEqual(2, len(template_list))
        self.assertIn(f1.name, template_set)
        self.assertIn(f2.name, template_set)

        shutil.rmtree(root)

    def test_render(self):
        content = "Hello World!"
        self.assertEqual(content, jinjaenv.get().render_string(content))

        content = "{% for i in range(10) %}{{ i }}{% endfor %}"
        self.assertEqual("0123456789", jinjaenv.get().render_string(content))

        content = "{% trans %}Pouac{% endtrans %}"
        self.assertEqual("Pouac", jinjaenv.get().render_string(content))

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

class JinjaenvTest(unittest.TestCase):
    def setUp(self):
        self.src_path  = tempfile.mkdtemp()
        jinjaenv.init(self.src_path)

    def tearDown(self):
        shutil.rmtree(self.src_path)

    def test_render_path(self):
        path = os.path.join(self.src_path, "_foo.html")

        # No variables
        with open(path, "w") as f:
            f.write("catch")
        filters.add_alias("blog", "_foo.html")
        self.assertEqual("catch", jinjaenv.get().render_relative_path("blog"))
        self.assertEqual("catch", jinjaenv.get().render_path(os.path.join(self.src_path, "blog")))

        # No variables
        with open(path, "w") as f:
            f.write("catch {{ times }}")
        filters.add_alias("blog", "_foo.html", {"times": 22})
        self.assertEqual(22, jinjaenv.get().get_variable("blog", "times"))

        jinjaenv.get().set_variable("_foo.html", "times", 32)
        self.assertEqual(32, jinjaenv.get().get_variable("_foo.html", "times"))
        self.assertEqual("catch 32", jinjaenv.get().render_template("_foo.html"))
        self.assertEqual("catch 32", jinjaenv.get().render_relative_path("_foo.html"))

        self.assertEqual("catch 42", jinjaenv.get().render_template("_foo.html", {"times": 42}))
        self.assertEqual("catch 22", jinjaenv.get().render_relative_path("blog"))

class ToolsTranslateTest(unittest.TestCase):
    def setUp(self):
        self.src_path = tempfile.mkdtemp()
        self.dst_path = tempfile.mkdtemp()
        subdir = os.path.join(self.src_path, "blog")
        os.mkdir(subdir)
        self.f1 = tempfile.NamedTemporaryFile(suffix=".html", dir=subdir, delete=False)
        self.f1.write("{% trans %}Hello World!{% endtrans %}")
        self.f1.flush()

    def tearDown(self):
        shutil.rmtree(self.src_path)
        shutil.rmtree(self.dst_path)

    def test_list_translatable_files(self):
        files = list(templates.list_translatable_files(self.src_path))
        self.assertEqual([self.f1.name], files)

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

class FiltersTest(unittest.TestCase):
    def test_filters_are_registered(self):
        env = jinjaenv.get()._jinja_env
        self.assertIn("set_date", env.filters.keys())
        self.assertIn("get_date", env.filters.keys())
        self.assertEqual(filters.set_date, env.filters["set_date"])
        self.assertEqual(filters.get_date, env.filters["get_date"])

    def test_set_date(self):
        string = "{{ 'Title'|set_date('2013-11') }}"
        result = jinjaenv.get().render_string(string)
        self.assertEqual("", result)
        self.assertEqual("2013-11", filters.get_date("Title"))

    def test_date_variables(self):
        # Set-get
        filters.set_date("foo", "1901")
        self.assertEqual("1901", filters.get_date("foo"))

        # Set-get via config file
        root = tempfile.mkdtemp()
        config_path = os.path.join(root, "_config.html")
        with open(config_path, "w") as f:
            f.write("{{ 'pouac'|set_date('2013-11-01') }}\n")
            f.write("{{ 'prout'|set_date('2013-10-01 18:15') }}")

        jinjaenv.init(root)

        self.assertEqual("2013-11-01", filters.get_date("pouac"))
        self.assertEqual(["pouac"], filters.latest_pages(1))
        self.assertEqual(["pouac", "prout"], filters.latest_pages(2))

        shutil.rmtree(root)

def main():
    unittest.main()

if __name__ == "__main__":
    main()
