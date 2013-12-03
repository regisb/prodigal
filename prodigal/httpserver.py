import os
import posixpath
import urllib
import BaseHTTPServer
import SimpleHTTPServer
from StringIO import StringIO

import jinjaenv
import templates
import translate

class HttpRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    JINJAENV    = None
    ROOT_PATH   = None
    LOCALE      = None

    @property
    def jinjaenv(self):
        if HttpRequestHandler.JINJAENV is None:
            HttpRequestHandler.JINJAENV = jinjaenv.get(HttpRequestHandler.ROOT_PATH,
                                                       HttpRequestHandler.LOCALE)
        return HttpRequestHandler.JINJAENV

    def do_GET(self):
        f = self.send_head()
        if f:
            if hasattr(f, "name") and templates.should_render(f.name):
                # Compile template
                template_name = os.path.relpath(f.name, HttpRequestHandler.ROOT_PATH)
                template = self.jinjaenv.get_template(template_name)
                rendered = template.render().encode("utf-8")
                self.copyfile(StringIO(rendered), self.wfile)
            else:
                self.copyfile(f, self.wfile)

            f.close()

    def translate_path(self, path):
        """translate_path

        :param path:
        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = HttpRequestHandler.ROOT_PATH
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

def serve(src_path, locale, address):
    HttpRequestHandler.ROOT_PATH    = os.path.abspath(src_path)
    HttpRequestHandler.LOCALE       = locale
    translate.compile_if_possible(src_path, locale)

    ip, port = address.split(":")
    server_address = (ip, int(port))

    HttpRequestHandler.protocol_version = "HTTP/1.0"
    httpd = BaseHTTPServer.HTTPServer(server_address, HttpRequestHandler)

    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    httpd.serve_forever()
