import os.path
from babel.messages.catalog import Catalog
from babel.messages.pofile import write_po, read_po
from babel.messages.mofile import write_mo
from jinja2.ext import babel_extract
from StringIO import StringIO

class Translator(object):
    def __init__(self):
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
                sort_output=False, sort_by_file=False, ignore_obsolete=False,
                include_previous=False)
        po_content = stringio.getvalue()
        stringio.close()
        return po_content

    def write_po(self, path):
        with open(path, "w") as f:
            f.write(self.get_po())

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
