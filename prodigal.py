#! /usr/bin/env python
import argparse
import os.path
import jinja2
import gettext
#from glob import glob

#def find_files(path):
    #"""find_files
    #Find all files located in the current path and return an iterable on all the
    #absolute file paths.

    #:param path:
    #"""
    #files = glob(os.path.join(path, "*"))
    #print files
    #return map(os.path.abspath, files)

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

def prodigal(src_path, dst_path):
    jinja_env = get_jinja_env(src_path)
    for template_name in jinja_env.loader.list_templates():
        # Skip non-html files
        file_ext = os.path.splitext(template_name)[1]
        if file_ext != ".html":
            continue

        # Compile template
        template = jinja_env.get_template(template_name)
        print template.render()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="An awesome static website generator")
    parser.add_argument("src_path", help="Path of source files")
    parser.add_argument("dst_path", help="Path of destination files")
    args = parser.parse_args()

    prodigal(args.src_path, args.dst_path)
