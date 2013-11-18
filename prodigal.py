#! /usr/bin/env python
import argparse
import os.path
import logging
import sys
import jinja2
import babel.support
from translate import Translator
from translate import compile as compile_translations

def get_jinja_env(src_path=None):
    """get_jinja_env
    Get the jinja2 environment required to compile templates.
    """
    if src_path is not None:
        template_loader = jinja2.FileSystemLoader(src_path)
    else:
        template_loader = jinja2.BaseLoader()
    jinja_env = jinja2.Environment(loader=template_loader,
                                   extensions=['jinja2.ext.i18n'])
    return jinja_env

def install_translations(jinja_env, src_path, locale):
    with open(os.path.join(src_path, locale + ".mo")) as f:
            translations = babel.support.Translations(f)
            jinja_env.install_gettext_translations(translations)

def render(content):
    """render
    Compile and render a string.

    :param content:
    """
    return get_jinja_env().from_string(content).render()

def translate_content(locale, src_path):
    jinja_env = get_jinja_env(src_path)
    translator = Translator()
    for template_name in jinja_env.loader.list_templates():
        translator.add_file(os.path.join(src_path, template_name))
    # Save .po file
    po_path = os.path.join(src_path, locale + ".po")
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
    jinja_env = get_jinja_env(src_path)

    if locale is not None:
        compile_locale(src_path, locale)
        install_translations(jinja_env, src_path, locale)

    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    for template_name in jinja_env.loader.list_templates():
        # Skip non-html files
        # TODO not a good idea, but how to exclude .*.swp files?
        file_ext = os.path.splitext(template_name)[1]
        if file_ext != ".html":
            continue

        # Compile template
        template = jinja_env.get_template(template_name)
        rendered = template.render()

        # Save
        # TODO create directory if it doesn't exist
        # TODO delete extraneous files
        dst_file_path = os.path.join(dst_path, template_name)
        with open(dst_file_path, "w") as f:
            f.write(rendered)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prodigal: Yet another static website generator!")

    subparsers = parser.add_subparsers(dest="command", help="")

    parser_generate = subparsers.add_parser("generate",
            help="Generate a static website")
    parser_generate.add_argument("src_path",
            help="Path of source files")
    parser_generate.add_argument("dst_path",
            help="Path of destination files")
    parser_generate.add_argument("-l", "--locale",
            help="Locale of the generated content")

    parser_translate = subparsers.add_parser("translate",
            help="Produce the translation files for the static website")
    parser_translate.add_argument("locale",
            help="Locale code for generated translation files. E.g: fr, en_US.")
    parser_translate.add_argument("src_path",
            help="Path of source files")

    args = parser.parse_args()

    if args.command == "generate":
        generate(args.src_path, args.dst_path, args.locale)
    elif args.command == "translate":
        translate_content(args.locale, args.src_path)
