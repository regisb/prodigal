#! /usr/bin/env python
import os.path
import logging
import sys

import translate
import jinjaenv
import templates
import httpserver

def translate_templates(locale, src_path):
    """translate_templates
    Save locale strings to a locale.po translation file.

    :param locale:
    :param src_path:
    """
    po_path = os.path.join(src_path, locale + ".po")
    translator = translate.Translator(po_path)
    for template_name in templates.list_translatable_names(src_path):
        path = os.path.join(src_path, template_name)
        translator.add_file(path)
    translator.write_po(po_path)

def compile_locale(src_path, locale):
    po_file_path = os.path.join(src_path, locale + ".po")
    if not os.path.exists(po_file_path):
        if len(sys.argv) > 0:
            logging.warning("Locale file %s does not exist yet. You probably need to run \
                    '%s translate %s %s' first." % \
                    (po_file_path, sys.argv[0], locale, src_path))
            return
    translate.compile(po_file_path)

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
    jinjaenv.init(src_path, locale)
    env = jinjaenv.get()
    for url in env.renderable_urls():
        # Render
        rendered = env.render_path(url)
        if rendered is None:
            print "Warning: Could not find template for url", url
            continue

        # Save
        template_name = env.template_name(url)
        if os.path.splitext(template_name)[1] == '':
            template_name = os.path.join(template_name, "index.html")
        dst_file_path = os.path.join(dst_path, template_name)
        dst_dirname = os.path.dirname(dst_file_path)
        if not os.path.exists(dst_dirname):
            os.makedirs(dst_dirname)
        with open(dst_file_path, "w") as f:
            f.write(rendered)

def serve(src_path, locale, address):
    """serve
    Run a simple HTTP server that renders templates dynamically.

    :param src_path:
    :param locale:
    :param address:
    """

    return httpserver.serve(src_path, locale, address)
