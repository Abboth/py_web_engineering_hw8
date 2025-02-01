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
            case "/search":  # 🔥 Добавляем обработку запроса
                self.handle_search(route)
            case _:
                file = BASE_DIR.joinpath(route.path[1:])
                if file.exists():
                    self.send_static()
                else:
                    self.send_html_file("error.html", status=404)

    def handle_search(self, route):
        query_params = urllib.parse.parse_qs(route.query)
        search_query = query_params.get("query", [""])[0]

        if not search_query:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing query parameter")
            return

        # Отправляем запрос на сокет-сервер
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SOCKET_HOST, SOCKET_PORT))
        client_socket.sendall(search_query.encode())

        # Получаем ответ
        response_data = client_socket.recv(BUFFER_SIZE).decode()
        client_socket.close()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(response_data.encode())

    def do_POST(self):
        data = self.rfile.read(self.headers["Content-Length"])

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SOCKET_HOST, SOCKET_PORT))
        client_socket.sendall(data)

        response_data = client_socket.recv(BUFFER_SIZE)

        client_socket.close()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(response_data)

    def send_html_file(self, filename, status=200):
        html_path = Path("templates") / filename
        self.send_response(status)
        self.send_header("Content-Type", "text/templates")
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


def up_http(host, port):
    address = (host, port)
    server = HTTPServer(address, HttpHandler)  # type: ignore
    logging.info(f"HTTP server started at {address}")
    try:
        server.serve_forever()
    except KeyboardInterrupt as e:
        server.server_close()
        logging.error(f"error while serving: {e}")


def up_socket(host: str, port: int) -> None:
    address = (host, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(address)
    logging.info(f"Socket server started at {address}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(message)s")

    th_socket = Thread(target=up_socket, args=(SOCKET_HOST, SOCKET_PORT))
    th_http = Thread(target=up_http, args=(HTTP_HOST, HTTP_PORT))
    th_socket.start()
    th_http.start()

