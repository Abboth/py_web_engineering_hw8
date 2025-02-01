import socket
from data_selects.find import find_in_documents


def client(host: str, port: int, message: str) -> str:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    client_socket.sendall(message.encode())

    response = client_socket.recv(1024).decode()

    client_socket.close()
    return response
