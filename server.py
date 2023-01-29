import pickle
import socket
import threading

# sys.path.append('../src')
from Payload import Payload

IP = "localhost"
PORT = 8016
ADDR = (IP, PORT)
MSG_SIZE = 4096
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"

all_connections = {}

payload = Payload()  # Initialize payload


def handle_pond(connection, address):
    print(f"New pond connected from : {address}")
    connected = True
    while connected:
        try:
            message = connection.recv(MSG_SIZE)
        except ConnectionResetError:
            all_connections.pop(address, None)
            print(f"{address} Disconnects. Ponds in the vivisystem: {len(all_connections)}")
            break

        # separate message type
        try:
            msg = pickle.loads(message)
        except EOFError:
            all_connections.pop(address, None)
            print(f"{address} Disconnects. Ponds in the vivisystem: {len(all_connections)}")
            break

        print(f"New request From {address}, Action: {msg.action}")
        if msg.action == DISCONNECT_MSG:
            connected = False
            all_connections.pop(address)
            for conn in all_connections.values():
                # conn.send(f"{address} disconnected.".encode(FORMAT))
                print("-------------------------", msg.action)
                conn.send(message)
        else:
            for conn in all_connections.values():
                # print(msg)
                conn.send(message)
        print(f"Current connections {list(all_connections.keys())}")

    connection.close()


if __name__ == "__main__":
    print("Starting vivisystem...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen(5)
    print(f"Vivisystem is listening on {IP}:{PORT}")
    while True:
        add, con = server.accept()
        if type(add) == tuple:
            clientAddress = add
            clientConnection = con
        else:
            clientAddress = con
            clientConnection = add

        all_connections[clientAddress] = clientConnection

        pond_handler = threading.Thread(
            target=handle_pond,
            args=(
                clientConnection,
                clientAddress,
            ),
        )
        pond_handler.start()
        print(
            f"Ponds in the vivisystem: {threading.active_count() - 1} {clientConnection} {clientAddress}"
        )
