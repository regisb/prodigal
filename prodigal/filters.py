import sys
import inspect
from collections import defaultdict

import media

ALIASES = defaultdict(dict)
BLOG_TEMPLATE = None

def filter(fn):
    fn.is_filter = True
    return fn

def template_alias(template_name):
    for alias, properties in ALIASES.iteritems():
        if properties.get("template_name") == template_name:
            return alias
    return template_name

@filter
def template_name(alias):
    if alias in ALIASES and "template_name" in ALIASES[alias]:
        return ALIASES[alias]["template_name"]
    return alias

@filter
def template_href(template_name):
    return "/" + template_alias(template_name)

@filter
def set_date(template_name, date):
    global ALIASES
    ALIASES[template_name]["date"] = date
    return ""

@filter
def get_date(template_name):
    global ALIASES
    return ALIASES[template_name].get("date")

@filter
def set_title(template_name, title):
    global ALIASES
    ALIASES[template_name]["title"] = title
    return ""

@filter
def get_title(template_name):
    global ALIASES
    return ALIASES[template_name].get("title")

@filter
def latest_pages(count):
    dates = [(d["date"], n) for n, d in ALIASES.iteritems() if "date" in d]
    dates.sort(reverse=True)
    return [d[1] for d in dates[:count]]

@filter
def add_alias(alias, template_name, variables={}):
    global ALIASES
    ALIASES[alias] = {
            "template_name": template_name,
            "variables": variables
    }
def get_alias(url):
    return ALIASES.get(url)
def list_aliases():
    for alias, properties in ALIASES.iteritems():
        yield alias
    raise StopIteration

@filter
def set_blog_template(template_name):
    global BLOG_TEMPLATE
    BLOG_TEMPLATE = template_name

@filter
def add_blog_post(template_name, alias, title, date):
    add_alias(alias, BLOG_TEMPLATE, {"post": template_name})
    set_title(alias, title)
    set_date(alias, date)
    return ""
@filter
def blog_post_template_name(alias):
    if alias in ALIASES:
        properties = ALIASES[alias]
        if "variables" in properties:
            if "post" in properties["variables"]:
                return properties["variables"]["post"]
    return None

@filter
def add_media(folder):
    media.add(folder)

def init():
    global ALIASES, BLOG_TEMPLATE
    ALIASES = defaultdict(dict)
    BLOG_TEMPLATE = None

def register_all(env):
    # List all functions with @filter decorator
    module = sys.modules[__name__]
    for (fn_name, fn) in inspect.getmembers(module, inspect.isfunction):
        if hasattr(fn, "is_filter"):
            env.filters[fn_name] = fn

