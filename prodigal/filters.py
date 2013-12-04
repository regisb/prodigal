import sys
import inspect

def filter(fn):
    fn.is_filter = True
    return fn

@filter
def pouac(value):
    return value + " Pouac!"

TEMPLATE_DATES = {}
@filter
def set_date(template_name, date):
    global TEMPLATE_DATES
    TEMPLATE_DATES[template_name] = date

@filter
def latest_pages(count):
    dates = [(d, n) for n, d in TEMPLATE_DATES.iteritems()]
    dates.sort(reverse=True)
    return [d[1] for d in dates[:count]]

def register_all(env):
    # List all functions with @filter decorator
    module = sys.modules[__name__]
    for (fn_name, fn) in inspect.getmembers(module, inspect.isfunction):
        if hasattr(fn, "is_filter"):
            env.filters[fn_name] = fn

