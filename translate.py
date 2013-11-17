import os.path
from babel.messages.catalog import Catalog
from babel.messages.pofile import write_po
from jinja2.ext import babel_extract
from StringIO import StringIO

class Translator(object):
    def __init__(self):
        self.catalog = Catalog(project="The Awesome Project",
                version="v42",
                msgid_bugs_address=None,
                copyright_holder=None,
                charset="utf-8")
        self.src_path = None

    def add_messages(self, extracted):
        for filename, lineno, message, comments in extracted:
            location = []
            if self.src_path is not None:
                filepath = os.path.normpath(os.path.join(self.src_path, filename))
                location = [(filepath, lineno)]
            self.catalog.add(message, None, location,
                    auto_comments=comments)

    def add(self, message):
        # Parse messages to translate
        stringio = StringIO(message)
        extracted = list(babel_extract(stringio, ('gettext', 'ngettext', '_'), [], {}))

        # Add messages to translate to catalog
        self.add_messages(extracted)

    def get_po(self):
        stringio = StringIO()
        write_po(stringio, self.catalog, width=76, no_location=False, omit_header=True,
                sort_output=False, sort_by_file=False, ignore_obsolete=False,
                include_previous=False)
        po_content = stringio.getvalue()
        stringio.close()
        return po_content
