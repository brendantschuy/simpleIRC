import socket
import select
import sys

from config import *

OPS_MAP = {
    "!join" : JOIN_ROOM,
    "!namechange" : NAME_CHANGE,
    "!create" : CREATE_ROOM,
    "!leave" : LEAVE_ROOM,
    "!room" : SEND_TO_ROOM,
    "!pm" : PRIVATE_MESSAGE
}

def showHelp():
    print("========================== HELP ========================\n" \
        f"{'!namechange <name>': <20} {'change your name to <name>': >35}\n"\
        f"{'!create <name>': <20} {'create room <name>': >35}\n"\
        f"{'!join <name>': <20} {'join room <name>': >35}\n"\
        f"{'!leave <name>': <20} {'leave room <name>': >35}\n"\
        f"{'!room <name>': <20} {'send chat to room <name>': >35}\n"\
        f"{'!pm <user> <msg>': <20} {'private message': >35}\n"\
        f"{'!members <room>': <20} {'list members of room': >35}\n"\
        f"{'!rooms': <20} {'list all rooms': >35}\n"\
        f"{'!online': <20} {'list all online users': >35}\n"\
        f"{'!dc': <20} {'disconnect from server': >35}\n"\
            )

def send(msg, op):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    opbytes = str(op).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    server.send(send_length)
    server.send(opbytes)
    server.send(message)

def decodeOp(msg):
    op = msg.split(' ')[0].strip()
    if(not op[:1] == "!"):
        return msg, SEND_MESSAGE
    if(op == "!dc"):
        return msg, DISCONNECT
    if op == "!help":
        showHelp()
        return False, False
    if op == "!rooms":
        return msg, LIST_ROOMS
    if op == "!members":
        return msg, LIST_MEMBERS
    if op == "!online":
        return msg, LIST_ONLINE
    if op in OPS_MAP:
        msg = " ".join(msg.split(' ')[1:])
        return msg, OPS_MAP[op]
    else:
        raise "OOPS"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(FULL_ADDRESS)

user = input("Enter a username: ")
send(user, JOIN_SERVER)

print("> ", end='')

while True:
    try:
        socketList = [ sys.stdin, server ]
        reads, writes, error = select.select(socketList, [], [])

        for skt in reads:
            if skt == sys.stdin:
                try:
                    line = sys.stdin.readline().strip()
                    msg, op = decodeOp(line)
                    if(op):
                        send(msg, op)
                except:
                    print("Unknown op code. Type !help for more information.")
                    continue
                if(op == DISCONNECT):
                    print("Disconnecting from server...")
                    exit()
            else:
                data = skt.recv(2048)
                if(data):
                    rcvd = data.decode(FORMAT).strip()
                    if(rcvd == "XXXX"):
                        print("Server has disconnected. 😵")
                        exit()
                    print(f"{rcvd}")
                    print("> ", end='')
    except:
        # mainly handle SIGINTs
        send("", DISCONNECT)
        exit()
