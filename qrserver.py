import http.server
import socketserver
import re

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        valid_path = re.search("\/orders\?oid=\d+", self.path)

        if valid_path:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Hello, world!")
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not found")

PORT = 8000

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()