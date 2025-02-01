import socket
import logging
from data_selects.find import find_in_documents


def echo_server(host: str, port: int) -> None:
    sock = socket.socket()

    server = host, port
    sock.bind(server)
    sock.listen()

    logging.info(f"Echo Server started on {host}:{port}")
    try:
        while True:
            conn, addr = sock.accept()
            with conn:
                data = conn.recv(1024)
                if not data:
                    continue
                parsed_data = find_in_documents(data)
                conn.send(parsed_data.encode())

    except KeyboardInterrupt:
        logging.info(f"Echo Server stopped")
    finally:
        sock.close()
