import os.path
import babel.support
import gettext
import jinja2

import filters

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

def _render_variables(env, src_path):
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

def get(src_path=None, locale=None):
    """get
    Get the jinja2 environment required to compile templates.
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

