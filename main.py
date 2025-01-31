from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from pathlib import Path
import urllib.parse
import mimetypes
import logging
import socket

BASE_DIR = Path()
HTTP_PORT = 3000
HTTP_HOST = "0.0.0.0"
SOCKET_PORT = 5000
SOCKET_HOST = "localhost"
BUFFER_SIZE = 1024


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        match route.path:
            case "/" | "/index.html":
                self.send_html_file("index.html")
            case "/message.html":
                self.send_html_file("message.html")
            case "/message_successfully.html":
                self.send_html_file("message_successfully.html")
            case _:
                file = BASE_DIR.joinpath(route.path[1:])
                if file.exists():
                    self.send_static()
                else:
                    self.send_html_file("error.html", status=404)

    def send_html_file(self, filename, status=200):
        html_path = Path("templates") / filename
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        with open(html_path, "r", encoding="utf-8") as f:
            self.wfile.write(f.read().encode())

    def send_static(self):
        static_path = Path("statics") / Path(self.path).relative_to("/statics")
        if not static_path.exists() or not static_path.is_file():
            logging.info(f"Static file not found: {static_path}")
            self.send_error(404, "Static file not found")
            return
        self.send_response(200)
        mime_type, _ = mimetypes.guess_type(static_path)
        self.send_header("Content-Type", mime_type or "application/octet-stream")
        self.end_headers()
        with open(static_path, "rb") as file:
            self.wfile.write(file.read())
