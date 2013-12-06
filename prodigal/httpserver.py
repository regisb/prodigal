import os
import posixpath
import urllib
import BaseHTTPServer
import SimpleHTTPServer
from cStringIO import StringIO

import jinjaenv
import translate

class HttpRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    ROOT_PATH   = None
    LOCALE      = None
    TRANSLATION_UPDATER = None

    @property
    def locale(self):
        return HttpRequestHandler.LOCALE

    @property
    def translation_updater(self):
        if HttpRequestHandler.TRANSLATION_UPDATER is None:
            HttpRequestHandler.TRANSLATION_UPDATER = translate.Updater(HttpRequestHandler.ROOT_PATH,
                                                                       HttpRequestHandler.LOCALE)
        return HttpRequestHandler.TRANSLATION_UPDATER

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(jinjaenv.get().get_path(path))

        rendered = jinjaenv.get().render_path(path)
        if rendered is None:
            self.send_error(404, "File not found: " + path)
            return None

        # Content length and last-modified attributes
        #fs = os.fstat(f.fileno())
        #content_length = fs[6]
        #last_modified = self.date_time_string(fs.st_mtime)

        f = StringIO()
        f.write(rendered)
        content_length = f.tell()
        f.seek(0)

        self.send_response(200)
        self.send_header("Content-type", ctype)
        self.send_header("Content-Length", str(content_length))
        #self.send_header("Last-Modified", last_modified)
        self.end_headers()
        return f

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
        # The following line is the only part that differs from the
        # SimpleHTTPRequestHandler implementation
        path = HttpRequestHandler.ROOT_PATH
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

def serve(src_path, locale, address):
    jinjaenv.init(src_path, locale)
    HttpRequestHandler.ROOT_PATH    = os.path.abspath(src_path)
    HttpRequestHandler.LOCALE       = locale
    translate.compile_if_possible(src_path, locale)

    ip, port = address.split(":")
    server_address = (ip, int(port))

    HttpRequestHandler.protocol_version = "HTTP/1.0"
    httpd = BaseHTTPServer.HTTPServer(server_address, HttpRequestHandler)

    sa = httpd.socket.getsockname()
    print "Serving HTTP on", "http://" + sa[0] + ":" + str(sa[1]), "..."
    httpd.serve_forever()
