import sys
import inspect
import os.path
import babel.support
import gettext
import jinja2

import filters# TODO get rid of this circular dependency

class TemplateLoader(jinja2.loaders.BaseLoader):
    def __init__(self, src_path):
        self.src_path = os.path.abspath(src_path)
        self.aliases = {}

    def add_alias(self, alias, template_name):
        self.aliases[alias] = template_name

    def get_path(self, template_name):
        if template_name in self.aliases:
            return os.path.join(self.src_path, self.aliases[template_name])
        else:
            return os.path.join(self.src_path, template_name)

    def get_source(self, environment, template):
        path = self.get_path(template)
        ext = os.path.splitext(path)[1]
        if not os.path.exists(path) or ext != ".html":
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
        for alias, template_name in self.aliases.iteritems():
            paths.append(alias)
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
    module = sys.modules[filters.__name__]
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
        self._variables = {}

    def post_init(self):
        if self._src_path is not None:
            if os.path.exists(os.path.join(self._src_path, "_config.html")):
                self.render_template("_config.html")

    def set_variable(self, template_name, key, value):
        if template_name not in self._variables:
            self._variables[template_name] = {}
        self._variables[template_name][key] = value

    def get_variable(self, template_name, key):
        return self._variables.get(template_name, {}).get(key)

    def templates_with_variable(self, key):
        for template_name, properties in self._variables.iteritems():
            if key in properties:
                yield template_name, properties[key]

    def add_alias(self, alias, template_name, variables={}):
        self._variables[alias] = variables
        self._jinja_env.loader.add_alias(alias, template_name)

    def template_name(self, path):
        return os.path.relpath(os.path.abspath(path), self._src_path)

    def render_template(self, template_name, variables={}):
        try:
            template = self._jinja_env.get_template(template_name)
        except jinja2.exceptions.TemplateNotFound:
            return None

        varcopy = {"template_name": template_name}
        varcopy.update(self._variables.get(template_name, {}))
        varcopy.update(variables)
        return template.render(varcopy).encode("utf-8")

    def render_string(self, string):
        return self._jinja_env.from_string(string).render()

    def get_path(self, url):
        template_name = self.template_name(url)
        return self._jinja_env.loader.get_path(template_name)

    def render_relative_path(self, path):
        return self.render_path(os.path.join(self._src_path, path))

    def render_path(self, path):
        template_name = self.template_name(path)
        variables = self._variables.get(template_name, {})

        # 1) Try to render as a template
        rendered = self.render_template(template_name, variables)
        if rendered is not None:
            return rendered

        # 2) Just read the file
        path = os.path.join(self._src_path, template_name)
        if os.path.exists(path):
            return open(path, "rb").read()

        # 3) Man, we failed...
        return None

    def renderable_urls(self):
        for template_name in self._jinja_env.loader.list_templates():
            if not os.path.basename(template_name).startswith("_"):
                yield os.path.join(self._src_path, template_name)
        raise StopIteration

def init(src_path=None, locale=None):
    # TODO fix this somehow
    #filters.init()
    Environment._instance = Environment(src_path, locale)
    Environment._instance.post_init()

def reinit():
    src_path = Environment._instance._src_path
    locale = Environment._instance._locale
    init(src_path, locale)

def get():
    if Environment._instance is None:
        init()
    return Environment._instance
