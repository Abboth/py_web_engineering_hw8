import socket


def client(host: str, port: int) -> None:
    client_socket = socket.socket()
    client_socket.connect((host, port))
    msg = input(">>> ")

    while msg.lower().strip() != ["exit", "quit"]:
        client_socket.send(msg.encode())
        client_socket.recv(1024).decode()
        msg = input(f">>> ")

    client_socket.close()
