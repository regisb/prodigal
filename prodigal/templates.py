import os

def should_translate(path):
    """should_translate
    Return True if the template should be added to the list of files to
    translate. We translate only content from .html files.

    :param path:
    """
    return os.path.splitext(path)[1] == ".html"

def should_render(path):
    """should_render
    Return True if the template should be rendered (and moved to the
    destination directory later). We skip non-html files and files that start
    with "_".

    :param path:
    """
    if not should_translate(path):
        return False
    filename = os.path.basename(path)
    if filename.startswith("_"):
        return False
    return True

def list_files(src_path):
    """list_files
    List all files in the given path by walking the directory. Note that all
    files are returned, including non-renderable, non-translatable files.

    :param src_path:
    """
    for (dirpath, dirnames, filenames) in os.walk(src_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            yield file_path
    raise StopIteration

def list_renderable_files(src_path):
    for path in list_files(src_path):
        if should_render(path):
            yield path
    raise StopIteration

def list_translatable_names(src_path):
    for (dirpath, dirnames, filenames) in os.walk(src_path):
        for filename in filenames:
            if should_translate(filename):
                yield filename
    raise StopIteration
