#! /usr/bin/env python
import os.path
import logging
import sys

from translate import Translator
from translate import compile as compile_translations
import jinjaenv
import templates
import httpserver

def render(string):
    """render
    Compile and render a string.

    :param string:
    :param locale:
    """
    return jinjaenv.get().from_string(string).render()

def translate_templates(locale, src_path):
    """translate_templates
    Save locale strings to a locale.po translation file.

    :param locale:
    :param src_path:
    """
    po_path = os.path.join(src_path, locale + ".po")
    translator = Translator(po_path)
    for template_name in templates.list(src_path):
        if templates.should_translate(template_name):
            translator.add_file(template_name)
    translator.write_po(po_path)

def compile_locale(src_path, locale):
    po_file_path = os.path.join(src_path, locale + ".po")
    if not os.path.exists(po_file_path):
        if len(sys.argv) > 0:
            logging.warning("Locale file %s does not exist yet. You probably need to run \
                    '%s translate %s %s' first." % \
                    (po_file_path, sys.argv[0], locale, src_path))
            return
    compile_translations(po_file_path)

def generate(src_path, dst_path, locale=None):
    """generate
    Compile appropriate locale (if necessary) and then render all templates
    into the destination path.

    :param src_path:
    :param dst_path:
    :param locale:
    """
    src_path = os.path.abspath(src_path)
    dst_path = os.path.abspath(dst_path)
    if locale is not None:
        compile_locale(src_path, locale)
    generate_templates(src_path, dst_path, locale)

def generate_templates(src_path, dst_path, locale):
    jinja_env = jinjaenv.get(src_path, locale)
    for template_name in templates.list(src_path):
        if not templates.should_render(template_name):
            continue

        # Compile template
        template_name = os.path.relpath(template_name, src_path)
        template = jinja_env.get_template(template_name)
        rendered = template.render().encode("utf-8")

        # Save
        dst_file_path = os.path.join(dst_path, template_name)
        dst_dirname = os.path.dirname(dst_file_path)
        if not os.path.exists(dst_dirname):
            os.makedirs(dst_dirname)
        with open(dst_file_path, "w") as f:
            f.write(rendered)

def serve(src_path, locale):
    """serve
    Run a simple HTTP server that renders templates dynamically.

    :param src_path:
    :param locale:
    """

    return httpserver.serve(src_path, locale)
