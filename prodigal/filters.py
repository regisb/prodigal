import sys
import inspect

def filter(fn):
    fn.is_filter = True
    return fn

@filter
def pouac(value):
    return value + " Pouac!"

def register_all(env):
    # List all functions with @filter decorator
    module = sys.modules[__name__]
    for (fn_name, fn) in inspect.getmembers(module, inspect.isfunction):
        if hasattr(fn, "is_filter"):
            env.filters[fn_name] = fn

