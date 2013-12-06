import media
import jinjaenv

# TODO get rid of this global variable
BLOG_TEMPLATE = None

def filter(fn):
    """filter
    Filter decorator that will indicate that functions should be made available
    as filters in jinja2 templates.

    :param fn:
    """
    fn.is_filter = True
    return fn

@filter
def set_date(template_name, date):
    jinjaenv.get().set_variable(template_name, "date", date)
    return ""

@filter
def get_date(template_name):
    return jinjaenv.get().get_variable(template_name, "date")

@filter
def set_title(template_name, title):
    jinjaenv.get().set_variable(template_name, "title", title)
    return ""

@filter
def get_title(template_name):
    return jinjaenv.get().get_variable(template_name, "title")

@filter
def latest_pages(count):
    dates = [(d, t) for t, d in jinjaenv.get().templates_with_variable("date")]
    dates.sort(reverse=True)
    return [d[1] for d in dates[:count]]

@filter
def add_alias(alias, template_name, variables={}):
    jinjaenv.get().add_alias(alias, template_name, variables)

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
def blog_post_content(alias):
    return jinjaenv.get().get_variable(alias, "post")

@filter
def add_media(folder):
    media.add(folder)

def init():
    global BLOG_TEMPLATE
    BLOG_TEMPLATE = None
