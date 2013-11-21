#! /usr/bin/env python
import os.path
import logging
import sys
import jinja2
import babel.support
import gettext
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

def install_translations(jinja_env, src_path=None, locale=None):
    if locale is not None and src_path is not None:
        with open(os.path.join(src_path, locale + ".mo")) as f:
                translations = babel.support.Translations(f)
                jinja_env.install_gettext_translations(translations)
    else:
        jinja_env.install_gettext_translations(gettext)

def render(content):
    """render
    Compile and render a string.

    :param content:
    :param locale:
    """
    jinja_env = get_jinja_env()
    install_translations(jinja_env)
    return jinja_env.from_string(content).render()

def should_translate(path):
    """should_translate
    Return True if the template should be added to the list of files to
    translate. We translate only content from .html files.

    :param path:
    """
    return os.path.splitext(path)[1] == ".html"

def should_render(path):
    """should_render
    Return True if the template should be rendered (and moved to the
    destination directory later). We skip non-html files and files that start
    with "_".

    :param path:
    """
    if not should_translate(path):
        return False
    filename = os.path.basename(path)
    if filename.startswith("_"):
        return False
    return True

def translate_content(locale, src_path):
    jinja_env = get_jinja_env(src_path)
    translator = Translator()
    for template_name in jinja_env.loader.list_templates():
        if should_translate(template_name):
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
    generate_templates(jinja_env, dst_path)

def generate_templates(jinja_env, dst_path):
    for template_name in jinja_env.loader.list_templates():
        if not should_render(template_name):
            continue

        # Compile template
        template = jinja_env.get_template(template_name)
        rendered = template.render().encode("utf-8")

        # Save
        dst_file_path = os.path.join(dst_path, template_name)
        dst_dirname = os.path.dirname(dst_file_path)
        if not os.path.exists(dst_dirname):
            os.makedirs(dst_dirname)
        with open(dst_file_path, "w") as f:
            f.write(rendered)

