import socket
import ChessEngine
import pickle


class Network:

    def __init__(self):
        self.online = False
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "Enter IP of server here"
        self.port = 5555
        self.addr = (self.host, self.port)
        self.id = self.connect()
        self.moveMade = False
        self.isReady = False

    def connect(self):
        try:
            self.client.connect(self.addr)
            data = self.client.recv(2048).decode()
            print("Revieved: Color", data)
            self.online = True
            return data
        except:
            print("Server is offline")

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
        except socket.error as e:
            print(e)

    def disconnect():
        self.client.close()

    def reciveMoves(self):
        try:
            data = pickle.loads(self.client.recv(2048))
            return data
        except:
            pass

    def send_Ready(self):
        if self.id == "b":
            self.isReady = True
            return
        else:
            try:
                data = pickle.loads(self.client.recv(2048))
                if data == "Ready":
                    print("Recieved:", data)
                    self.isReady = True
            except:
                print("Disconnected from server")
