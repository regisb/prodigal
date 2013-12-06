import sys
import inspect
import os.path
import babel.support
import gettext
import jinja2

import filters
import templates

class TemplateLoader(jinja2.loaders.BaseLoader):
    def __init__(self, src_path):
        self.src_path = os.path.abspath(src_path)

    def get_source(self, environment, template):
        path = os.path.join(self.src_path, template)
        if not os.path.exists(path):
            raise jinja2.exceptions.TemplateNotFound(template)
        contents = open(path).read().decode('utf-8')
        mtime = os.path.getmtime(path)
        def uptodate():
            try:
                return os.path.getmtime(path) == mtime
            except OSError:
                return False
        return contents, path, uptodate

    def list_templates(self):
        paths = []
        for (dirpath, dirnames, filenames) in os.walk(self.src_path):
            for filename in filenames:
                path = os.path.join(dirpath, filename)
                ext = os.path.splitext(path)[1]
                if ext != ".html":
                    continue
                path = os.path.relpath(path, self.src_path)
                paths.append(path)
        return paths

def _install_translations(jinja_env, src_path=None, locale=None):
    """install_translations
    Load translations into the environment, such that it can render translated
    templates. Don't load anything if src_path or locale is None, but maintain
    an interface for translation.

    :param jinja_env:
    :param src_path:
    :param locale:
    """
    if locale is not None and src_path is not None:
        with open(os.path.join(src_path, locale + ".mo")) as f:
            translations = babel.support.Translations(f)
            jinja_env.install_gettext_translations(translations)
    else:
        jinja_env.install_gettext_translations(gettext)

def _register_filters(env):
    # List all functions with @filter decorator in filters module
    module = sys.modules["prodigal.filters"]
    for (fn_name, fn) in inspect.getmembers(module, inspect.isfunction):
        if hasattr(fn, "is_filter"):
            env.filters[fn_name] = fn

def _get_jinja_env(src_path=None, locale=None):
    """_get_jinja_env
    Get the jinja2 environment required to compile templates.

    :param src_path:
    :param locale:
    """
    if src_path is not None:
        template_loader = TemplateLoader(src_path)
    else:
        template_loader = jinja2.BaseLoader()
    env = jinja2.Environment(loader=template_loader,
                             extensions=['jinja2.ext.i18n'])
    _install_translations(env, src_path, locale)
    _register_filters(env)
    return env

class Environment(object):
    _instance = None

    def __init__(self, src_path=None, locale=None):
        self._src_path = None if src_path is None else os.path.abspath(src_path)
        self._locale = locale

        self._jinja_env = _get_jinja_env(self._src_path, self._locale)

        if os.path.exists(os.path.join(self._src_path, "_config.html")):
            self.render_template("_config.html")

    def template_name(self, path):
        return os.path.relpath(os.path.abspath(path), self._src_path)

    def render_template(self, template_name, variables={}):
        template = self._jinja_env.get_template(template_name)

        varcopy = variables.copy()
        if "template_name" not in varcopy:
            varcopy["template_name"] = template_name
        return template.render(varcopy).encode("utf-8")

    def render_string(self, string):
        return self._jinja_env.from_string(string).render()

    def url_template_name(self, url):
        relative_url = self.template_name(url)
        url = filters.get_alias(relative_url)
        if url is not None:
            return os.path.join(self._src_path, url["template_name"])
        return relative_url

    def render_relative_path(self, path):
        return self.render_path(os.path.join(self._src_path, path))

    def render_path(self, path):
        template_name = self.template_name(path)
        url_data = filters.get_alias(template_name)
        if url_data is not None:
            return self.render_template(url_data["template_name"], url_data["variables"])
        if templates.should_render(template_name) and template_name in self._jinja_env.list_templates():
            return self.render_template(template_name, {})
        path = os.path.join(self._src_path, template_name)
        if os.path.exists(path):
            return open(path, "rb").read()
        return None

    def renderable_urls(self):
        for path in templates.list_renderable_files(self._src_path):
            yield path
        for alias in filters.list_aliases():
            yield os.path.join(self._src_path, alias)
        raise StopIteration

def init(src_path=None, locale=None):
    if Environment._instance is not None:
        del(Environment._instance)
    filters.init()
    Environment._instance = Environment(src_path, locale)

def reinit():
    src_path = Environment._instance._src_path
    locale = Environment._instance._locale
    init(src_path, locale)

def get():
    if Environment._instance is None:
        init()
    return Environment._instance
