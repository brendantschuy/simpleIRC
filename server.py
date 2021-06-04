import socket
import threading

PORT = 5432
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
HEADER = 64
FORMAT = "utf-8"

DISCONNECT_MESSAGE = "!dc"

JOIN_SERVER = "0001"
SEND_MESSAGE = "0002"
JOIN_CHANNEL = "0003"
NAME_CHANGE = "0004"
DISCONNECT = "0005"
SERVER_CRASH = "XXXX"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)

clients = []

def broadcast(msg):
    for client in clients:
        client.send(msg)

def handleClient(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected")
    connected = True
    clients.append(conn)
    while(connected):
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            op = conn.recv(4).decode(FORMAT)

            msg = conn.recv(msg_length).decode(FORMAT)

            if(op == JOIN_SERVER):
                username = msg
                broadcast(f"{username} joined the server.".encode(FORMAT))
                print(f"{username} joined the server.")

            if(op == SEND_MESSAGE):
                broadcast(f"[{username}]: {msg}".encode(FORMAT))
                print(f"[{username}]: {msg}")

            if(op == NAME_CHANGE):
                broadcast(f"{username} changed their name to {msg}.".encode(FORMAT))
                print(f"{username} changed their name to {msg}.")
                username = msg 

            if(op == DISCONNECT):
                connected = False
                clients.remove(conn)
                broadcast(f"{username} left the server.".encode(FORMAT))
                print(f"{username} left the server.")
                break
            
            # conn.send("Msg received".encode(FORMAT))
    conn.close()

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        try:
            conn, addr = server.accept()
            thread = threading.Thread(target=handleClient, args=(conn, addr))
            thread.start()
            print(f"[NEW CONNECTION] active connections = {threading.activeCount() - 1}")
        except:
            #mainly handle SIGINTS
            print("We're crashing")
            broadcast(SERVER_CRASH.encode(FORMAT))
            exit()

print("[STARTING] Starting server...")
start()