import os.path
import babel.support
import gettext
import jinja2

import filters
import templates

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

def _render_variables(env, src_path=None):
    """_render_variables
    Render the content of the _variables file, which loads helpful variables
    such as the list of blog posts etc.

    :param env:
    :param src_path:
    """
    if src_path is not None:
        variables_name = "_variables"
        variables_path = os.path.join(src_path, variables_name)
        if os.path.exists(variables_path):
            env.get_template(variables_name).render()
            return True
    return False
def get_jinja_env(src_path=None, locale=None):
    """get_jinja_env
    Get the jinja2 environment required to compile templates.

    :param src_path:
    :param locale:
    """
    if src_path is not None:
        template_loader = jinja2.FileSystemLoader(src_path)
    else:
        template_loader = jinja2.BaseLoader()
    env = jinja2.Environment(loader=template_loader,
                             extensions=['jinja2.ext.i18n'])
    _install_translations(env, src_path, locale)
    filters.register_all(env)
    _render_variables(env, src_path)
    return env

class Environment(object):
    _instance = None

    def __init__(self, src_path=None, locale=None):
        self._src_path = None if src_path is None else os.path.abspath(src_path)
        self._locale = locale

        self._jinja_env = get_jinja_env(self._src_path, self._locale)

    def template_name(self, path):
        return os.path.relpath(os.path.abspath(path), self._src_path)

    def render_template(self, template_name, variables={}):
        template = self._jinja_env.get_template(template_name)
        return template.render(variables).encode("utf-8")

    def render_string(self, string):
        return self._jinja_env.from_string(string).render()

    def url_file_path(self, url):
        relative_url = self.template_name(url)
        url = filters.get_url(relative_url)
        if url is not None:
            return os.path.join(self._src_path, url["template_name"])
        return relative_url

    def render_path(self, path):
        url = self.template_name(path)
        return self.render_url(url)

    def render_url(self, url):
        url_data = filters.get_url(url)
        if url_data is not None:
            return self.render_template(url_data["template_name"], url_data["variables"])
        if templates.should_render(url) and url in self._jinja_env.list_templates():
            return self.render_template(url, {})
        path = os.path.join(self._src_path, url)
        if os.path.exists(path):
            return open(path, "rb").read()
        return None

    def renderable_template_names(self):
        for path in templates.list_renderable_files(self._src_path):
            yield self.template_name(path)

def init(src_path=None, locale=None):
    Environment._instance = Environment(src_path, locale)

def reinit():
    src_path = Environment._instance._src_path
    locale = Environment._instance._locale
    init(src_path, locale)

def get():
    if Environment._instance is None:
        init()
    return Environment._instance
