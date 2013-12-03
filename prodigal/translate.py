import os.path
from babel.messages.catalog import Catalog
from babel.messages.pofile import write_po, read_po
from babel.messages.mofile import write_mo
from jinja2.ext import babel_extract
from StringIO import StringIO

class Translator(object):
    def __init__(self, path=None):
        if path is not None and os.path.exists(path):
            # Load existing translations
            locale = os.path.splitext(os.path.basename(path))[0]
            with open(path) as f:
                self.catalog = read_po(f, locale)
        else:
            # Create new catalog
            self.catalog = Catalog(project="The Awesome Project",
                    version="v42",
                    msgid_bugs_address=None,
                    copyright_holder=None,
                    charset="utf-8")

    def add_messages(self, extracted, filepath=None):
        for lineno, funcname, message, comments in extracted:
            location = []
            if filepath is not None:
                location = [(filepath, lineno)]
            self.catalog.add(message, None, location,
                    auto_comments=comments)

    def _add(self, reader, filepath=None):
        # Parse messages to translate
        extracted = list(babel_extract(reader, ('gettext', 'ngettext', '_'), [], {}))
        # Add messages to translate to catalog
        self.add_messages(extracted, filepath=filepath)

    def add(self, message):
        self._add(StringIO(message))

    def add_file(self, filepath):
        with open(filepath) as f:
            self._add(f, filepath=filepath)

    def get_po(self):
        stringio = StringIO()
        write_po(stringio, self.catalog, width=76, no_location=False, omit_header=True,
                 sort_output=True, sort_by_file=True, ignore_obsolete=True,
                 include_previous=False)
        po_content = stringio.getvalue()
        stringio.close()
        return po_content

    def write_po(self, path):
        with open(path, "w") as f:
            f.write(self.get_po())

class Updater(object):
    def __init__(self, src_path, locale):
        self.src_path = src_path
        self.locale = locale

    @property
    def po_path(self):
        return os.path.join(self.src_path, self.locale + ".po")
    @property
    def mo_path(self):
        return os.path.join(self.src_path, self.locale + ".mo")
    def po_mtime(self):
        return os.stat(self.po_path).st_mtime
    def mo_mtime(self):
        return os.stat(self.mo_path).st_mtime

    def run(self):
        """run
        Compile the .po translation file if it was modified more recently than
        the .mo file.
        """
        if not os.path.exists(self.po_path):
            return False
        if os.path.exists(self.mo_path) and self.po_mtime() <= self.mo_mtime():
            return False

        # Compile locale file
        compile(self.po_path)
        return True

def compile(po_file_path):
    """compile
    Compile a xx.po file into an xx.mo file.

    :param po_file_path:
    """
    dirname  = os.path.dirname(po_file_path)
    filename = os.path.basename(po_file_path)
    locale   = os.path.splitext(filename)[0]
    mo_file_path = os.path.join(dirname, locale + ".mo")

    # Read catalog
    with open(po_file_path) as f:
        catalog = read_po(f, locale)

    # Write .mo file
    with open(mo_file_path, "w") as f:
        write_mo(f, catalog)

def compile_if_possible(src_path, locale):
    if locale is not None:
        po_path = os.path.join(src_path, locale + ".po")
        if os.path.exists(po_path):
            compile(po_path)
