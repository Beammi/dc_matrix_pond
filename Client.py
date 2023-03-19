import pickle
import random
import socket
import sys
import threading
import time
from typing import Callable

# sys.path.append('../src')
from FishData import FishData
from Payload import Payload
from PondData import PondData
from server import PORT

IP = "0.tcp.ap.ngrok.io"

ADDR = (IP, 12625)  # 19777
# IP = socket.gethostbyname(socket.gethostname())#"0.tcp.ap.ngrok.io"

# ADDR = (IP, PORT)
MSG_SIZE = 4096
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"


class Client:
    def __init__(self, pond: PondData, handle_migrate: Callable[[FishData], None]):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = IP
        self.port = PORT
        self.addr = ADDR
        self.connected = True
        self.other_ponds = {}
        self.disconnected_ponds = {}
        self.msg = self.connect()
        self.payload = Payload()
        self.pond = pond
        self.messageQ = []
        self.handle_migrate = handle_migrate

        msg_handler = threading.Thread(target=self.get_msg)
        msg_handler.start()
        send_handler = threading.Thread(target=self.send_pond)
        send_handler.start()

    def get_msg(self):
        return
        # while self.connected:
        #     time.sleep(0.5)
        #     msg: Payload = pickle.loads(self.client.recv(MSG_SIZE))
        #     print(f"received msg: {msg.action}, {msg.data}")
        #     if msg:
        #         self.messageQ.append(msg)
        #         self.handle_msg(msg)
        #     else:
        #         break

    def connect(self):
        try:
            self.client.connect(self.addr)
            print("Client connected ")
        except:
            print("Can not connect to the server")

    def send_pond(self):
        try:
            while self.connected:
                self.payload.action = "SEND"
                self.payload.data = self.pond
                print("POND >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> " + str(self.pond))
                # print("Client send :",self.pond)
                self.client.send(pickle.dumps(self.payload))
                time.sleep(2)

                # msg =  pickle.loads(self.client.recv(MSG_SIZE))
                # return self.handle_msg(msg)

        except socket.error as e:
            print(e)

    def migrate_random(self, fish: FishData) -> bool:
        print("trying to migrated")
        if not self.other_ponds:
            return False

        dest = random.choice(list(self.other_ponds.keys()))
        self._migrate_fish(fish, dest)
        return True

    def _migrate_fish(self, fishData, destination):
        # Migration takes a special object for the payload to pickup : The destination pond's name
        try:

            migration = {"destination": destination, "fish": fishData}
            self.payload.action = "MIGRATE"
            self.payload.data = migration

            self.client.send(pickle.dumps(self.payload))
            print("=======MIGRATED=======")
            # Handle our fish in the pond
            # // TO BE IMPLEMENTED

            # msg =  pickle.loads(self.client.recv(MSG_SIZE))
            # return self.handle_msg(msg)

            # print("Client send :",pond)
            # next_pond = random.random_choice(self.other_ponds.keys())
            # self.client.send("MIGRATE FROM sick_salmon TO "+ next_pond + " " + pickle.dumps(fishData))
            # msg =  pickle.loads(self.client.recv(MSG_SIZE))
            # return self.handle_msg(msg)
        except socket.error as e:
            print(e)

    def disconnect(self):
        try:
            self.connected = False
            self.payload.action = DISCONNECT_MSG
            print("Disconnecting...")
            self.client.send(pickle.dumps(self.payload))
            #            res = self.client.recv(MSG_SIZE)
            self.client.shutdown(socket.SHUT_RDWR)
            self.client.close()
        except socket.error as e:
            print(e)

    def handle_lifetime(self):
        while self.connected:
            if len(self.other_ponds.keys()) > 0:
                for k, v in self.other_ponds.items():
                    temp = self.other_ponds[k].fishes
                    for i in range(len(temp)):
                        temp[i].lifetime -= 1
                    self.other_ponds[k].fishes = []
                    for i in range(len(temp)):
                        if temp[i].lifetime > 0:
                            self.other_ponds[k].fishes.append(temp[i])

            time.sleep(1)

    def handle_msg(self, msg: Payload):
        msg_action = msg.action
        msg_object = msg.data
        print("handle_msg: ", msg.action)
        if msg_action == "SEND" and self.pond.pondName != msg_object.pondName:
            self.other_ponds[
                msg_object.pondName
            ] = msg_object  # Update in the dict key = pondname, values = <PondData>
            if msg_object.pondName in self.disconnected_ponds.keys():
                self.disconnected_ponds.pop(msg_object.pondName)
            print(self.other_ponds)
            return msg

        elif msg_action == "MIGRATE":
            if self.pond.pondName == msg_object["destination"]:
                print("=======RECIEVED MIGRATION=======")
                self.handle_migrate(msg_object["fish"])

        elif msg_action == DISCONNECT_MSG:
            print("DIS ACTION", msg_action)
            print("DIS OBJECT", msg_object)
            self.disconnected_ponds[msg_object.pondName] = msg_object
            self.other_ponds.pop(msg_object.pondName)

            # time.sleep(10)
        # print(self.other_ponds, self.disconnected_ponds)
        return msg

        # if msg[:7] == "MIGRATE":
        #     pass
        # elif msg[:4] == "JOIN":
        #     pass
        # elif msg[:11] == "DISCONNECT":
        #     pass
        # else:
        #     print(f"Vivisystem : {msg}")
        #     return msg


# for testing
if __name__ == "__main__":
    pond_name = sys.argv[1] if len(sys.argv) > 1 else "matrix-fish"
    p = PondData(pondName=pond_name)
    client = Client(p)
    while 1:
        f = FishData(pond_name)
        ok = client.migrate_random(f)
        print(f"Migrated: {ok}")
        time.sleep(3)
    # def __init__(self):
    #     self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     self.server = IP
    #     self.port = PORT
    #     self.addr = ADDR
    #     self.connected = True
    #     self.other_ponds = {}
    #     self.msg = self.connect()

    # def get_msg(self):
    #     return self.msg

    # def connect(self):
    #     try:
    #         self.client.connect(self.addr)
    #         print(f"Client connected ")
    #         return "Connected"
    #     except:
    #         print("Can not connect to the server")

    # def send_pond(self,pond):
    #     try:
    #         print("Client send :",pond)
    #         self.client.send(pickle.dumps(pond))
    #         msg =  pickle.loads(self.client.recv(MSG_SIZE))

    #         return self.handle_msg(msg)
    #     except socket.error as e:
    #         print(e)

    # def migrate_fish( self, fishData):
    #     try:
    #         print("Client send :",pond)
    #         next_pond = random.random_choice(self.other_ponds.keys())
    #         self.client.send("MIGRATE FROM sick_salmon TO "+ next_pond + " " + pickle.dumps(fishData))
    #         msg =  pickle.loads(self.client.recv(MSG_SIZE))
    #         return self.handle_msg(msg)
    #     except socket.error as e:
    #         print(e)

    # def handle_msg(self, msg):
    #     return msg
    #     if msg[:7] == "MIGRATE":
    #         pass
    #     elif msg[:4] == "JOIN":
    #         pass
    #     elif msg[:11] == "DISCONNECT":
    #         pass
    #     else:
    #         print(f"Vivisystem : {msg}")
    #         return msg
