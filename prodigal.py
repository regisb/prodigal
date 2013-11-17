#! /usr/bin/env python
import argparse
import os.path
import jinja2
import gettext
from translate import Translator

JINJA_ENV = None
def get_jinja_env(src_path=None):
    """get_jinja_env
    Get the jinja2 environment required to compile templates.
    """
    global JINJA_ENV
    if JINJA_ENV is None:
        # Create jinja environment
        if src_path is not None:
            template_loader = jinja2.FileSystemLoader(src_path)
        else:
            template_loader = jinja2.BaseLoader()
        JINJA_ENV = jinja2.Environment(loader=template_loader,
                                       extensions=['jinja2.ext.i18n'])
        JINJA_ENV.install_gettext_translations(gettext)
    return JINJA_ENV

def render(content):
    """render
    Compile and render a string.

    :param content:
    """
    return get_jinja_env().from_string(content).render()

def translate(language, src_path):
    jinja_env = get_jinja_env(src_path)
    translator = Translator(src_path)
    for template_name in jinja_env.loader.list_templates():
        translator.add_file(os.path.join(src_path, template_name))
    # Save .po file
    po_path = os.path.join(src_path, language + ".po")
    translator.write_po(po_path)

def generate(src_path, dst_path, language=None):
    jinja_env = get_jinja_env(src_path)
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
    parser_generate.add_argument("-l", "--language",
            help="Language of the generated content")

    parser_translate = subparsers.add_parser("translate",
            help="Produce the translation files for the static website")
    parser_translate.add_argument("language",
            help="Language code for generated translation files. E.g: fr, en_US.")
    parser_translate.add_argument("src_path",
            help="Path of source files")

    args = parser.parse_args()

    if args.command == "generate":
        generate(args.src_path, args.dst_path, args.language)
    elif args.command == "translate":
        translate(args.language, args.src_path)
