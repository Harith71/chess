import socket
from _thread import *
import sys
import pickle
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = "127.0.0.1"
port = 5555

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen()
print("[START] Waiting for a connection")

connections = 0
currentPlayer = 0

ips = []

move = []


def threaded_client(conn, player, total):
    reply = ""
    ready = False
    while True:
        if ready == False:
            if total % 2 == 0:
                ready = True
                reply = "Ready"
                try:
                    toSend = ips[player - 1]
                    toSend.sendall(pickle.dumps(reply))
                    reply = ""
                except:
                    pass
        try:
            data = pickle.loads(conn.recv(2040))
            move[player] = data
            if data and data != "Ready":
                #print("From Player " + str(player + 1) + " Recieved:", data)
                toSend = ips[player]
                if player % 2 == 1:
                    reply = move[player]
                    toSend = ips[player - 1]
                    #print("Sending To Player " + str(player) + " :", reply)
                else:
                    reply = move[player]
                    toSend = ips[player + 1]
                    #print("Sending To Player " + str(player + 2) + " :", reply)
                toSend.sendall(pickle.dumps(reply))
        except:
            pass


def assignColor(conn, player):
    color = ""
    if connections % 2 == 0:
        color = "b"
        conn.send(color.encode())
    else:
        color = "w"
        conn.send(color.encode())


while True:
    if connections < 8:
        conn, addr = s.accept()
        connections += 1
        ips.append(conn)
        print("[CONNECT] New connection:", addr)
        move.append("p" + str(connections))
        assignColor(conn, currentPlayer)
        start_new_thread(threaded_client, (conn, currentPlayer, connections))
        currentPlayer += 1
