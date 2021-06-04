import socket
import threading

PORT = 5432
SERVER = '127.0.0.1'
FULL_ADDRESS = (SERVER, PORT)
HEADER = 64
OP_LENGTH = 4
FORMAT = "utf-8"

JOIN_SERVER = "0001"
SEND_MESSAGE = "0002"
JOIN_ROOM = "0003"
NAME_CHANGE = "0004"
DISCONNECT = "0005"
CREATE_ROOM = "0006"
SEND_TO_ROOM = "0007"
LEAVE_ROOM = "0008"
PRIVATE_MESSAGE = "0009"
LIST_ROOMS = "0010"
LIST_MEMBERS = "0011"
LIST_ONLINE = "0012"

SERVER_CRASH = "XXXX"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind(FULL_ADDRESS)

clients = []
rooms = {}
users = {}

def broadcast(msg):
    print(msg.decode(FORMAT))
    for client in clients:
        client.send(msg)

def broadcastToRoom(room, msg):
    fullMsg = f"<{room}>{msg}"
    print(fullMsg)
    for client in rooms[room]:
        client.send(fullMsg.encode(FORMAT))
    

def createRoom(name, client, user):
    print(f"[CREATE ROOM] {user} created room {name}.")
    client.send(f"You created and joined the room {name}.\n".encode(FORMAT))
    rooms[name] = [client]

def joinRoom(name, client, user):
    if name not in rooms:
        client.send(f"Room {name} does not exist.".encode(FORMAT))
        print(f"Room {name} does not exist.")
        return False
    else:
        if client in rooms[name]:
            client.send(f"You are already in the room {name}.".encode(FORMAT))
            return False
        else:
            client.send(f"You joined the room {name}.".encode(FORMAT))
            print(f"{user} joined the room {name}.")
            rooms[name].append(client)
            return True

def leaveRoom(activeRooms, room, client):
    try:
        rooms[room].remove(client)
        client.send(f"You left the room {room}".encode(FORMAT))
        return activeRooms.remove(room)
    except:
        client.send(f"You are not in the room {room}.".encode(FORMAT))
        return activeRooms

def leaveAllRooms(client):
    for room in rooms:
        if client in rooms:
            rooms[room].remove(client)

def sendToRoom(msg, client, user, activeRooms):
    room = msg.split(" ")[0]
    msg = " ".join(msg.split(" ")[1:])
    if room not in activeRooms:
        client.send(f"You are not in the room {room}".encode(FORMAT))
    else:
        broadcastToRoom(room, f"[{user}]: {msg}")

def privateMessage(msg, client, user):
    target = msg.split(" ")[0]
    msg = " ".join(msg.split(" ")[1:])
    print(f"{user} is attempting to private message {target}.")
    if target not in users:
        client.send(f"{target} is not online.".encode(FORMAT))
    else:
        print(f"{user} private messaged {target}: {msg}")
        users[target].send(f"[{user}] private messaged you: {msg}".encode(FORMAT))

def listRooms(client):
    if not rooms:
        client.send("There are no rooms on this server.".encode(FORMAT))
    else:
        client.send(f"All available rooms: ".encode(FORMAT))
        for room in rooms:
            client.send(f"{room}\n".encode(FORMAT))

def listOnline(client):
    client.send(f"Currently online users: ".encode(FORMAT))
    for user in users:
        client.send(f"{user}\n".encode(FORMAT))

def listMembers(room, client):
    room = " ".join(room.split(" ")[1:])
    if room not in rooms:
        client.send(f"Room {room} not found.".encode(FORMAT))
    else:
        if not rooms[room]:
            client.send(f"No members in {room}.".encode(FORMAT))
        else:
            client.send(f"Members of {room}:\n".encode(FORMAT))
            for conn in rooms[room]:
                for user in users:
                    if(conn == users[user]):
                        client.send(f"{user}\n".encode(FORMAT))

def handleClient(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected")

    activeRooms = []
    connected = True
    username = ''

    clients.append(conn)
    while(connected):
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            op = conn.recv(OP_LENGTH).decode(FORMAT)

            msg = conn.recv(msg_length).decode(FORMAT)

            if op == JOIN_SERVER:
                username = msg
                broadcast(f"{username} joined the server.".encode(FORMAT))
                users[username] = conn

            if op == SEND_MESSAGE:
                broadcast(f"[{username}]: {msg}".encode(FORMAT))

            if op == NAME_CHANGE:
                broadcast(f"{username} changed their name to {msg}.".encode(FORMAT))
                username = msg 

            if op == CREATE_ROOM:
                createRoom(msg, conn, username)
                activeRooms.append(msg)

            if op == JOIN_ROOM:
                if(joinRoom(msg, conn, username)):
                    activeRooms.append(msg)

            if op == SEND_TO_ROOM:
                sendToRoom(msg, conn, username, activeRooms)

            if op == LEAVE_ROOM:
                activeRooms = leaveRoom(activeRooms, msg, conn)

            if op == PRIVATE_MESSAGE:
                privateMessage(msg, conn, username)

            if op == LIST_ROOMS:
                listRooms(conn)

            if op == LIST_MEMBERS:
                listMembers(msg, conn)

            if op == LIST_ONLINE:
                listOnline(conn)

            if op == DISCONNECT:
                connected = False
                clients.remove(conn)
                del users[username]
                leaveAllRooms(conn)
                broadcast(f"{username} left the server.".encode(FORMAT))
                print(f"[DISCONNECT] {username} left the server.")
                break

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
            # mainly handle SIGINTS
            print("\nServer crashed... 😵😵😵")
            broadcast(SERVER_CRASH.encode(FORMAT))
            exit()

print("[STARTING] Starting server...")
start()