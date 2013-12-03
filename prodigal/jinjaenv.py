import os.path
import babel.support
import gettext
import jinja2

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

def get(src_path=None, locale=None):
    """get
    Get the jinja2 environment required to compile templates.
    """
    if src_path is not None:
        template_loader = jinja2.FileSystemLoader(src_path)
    else:
        template_loader = jinja2.BaseLoader()
    jinja_env = jinja2.Environment(loader=template_loader,
                                   extensions=['jinja2.ext.i18n'])
    _install_translations(jinja_env, src_path, locale)
    return jinja_env

