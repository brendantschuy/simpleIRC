import socket
import select
import sys

PORT = 5432
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
HEADER = 64
FORMAT = "utf-8"
SERVER = "127.0.0.1"


SET_USERNAME = "0001"
SEND_MESSAGE = "0002"
JOIN_CHANNEL = "0003"
NAME_CHANGE = "0004"
DISCONNECT = "0005"

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
    msg = msg.split(' ')[1]
    print("op = ", op)
    print("msg = ", msg)
    if(op == "!namechange"):
        print("name change")
        return msg, NAME_CHANGE
    if(op == "!joinchannel"):
        return msg, JOIN_CHANNEL
    
def prompt():
    msg_str = input("> ")
    msg, op = decodeOp(msg_str)
    send(msg, op)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(ADDR)

user = input("Enter a username: ")
send(user, SET_USERNAME)

print("> ", end='')

while True:
    try:
        # print("> ", end='')
        socketList = [ sys.stdin, server ]
        reads, writes, error = select.select(socketList, [], [])

        for skt in reads:
            if skt == sys.stdin:
                line = sys.stdin.readline().strip()
                msg, op = decodeOp(line)
                send(msg, op)
                if(op == DISCONNECT):
                    print("Disconnecting from server...")
                    exit()
            else:
                data = skt.recv(2048)
                if(data):
                    rcvd = data.decode(FORMAT).strip()
                    if(rcvd == "XXXX"):
                        print("Server has disconnected.")
                        exit()
                    print(f"{rcvd}\n")
                    print("> ", end='')
    except:
        #mainly handle SIGINTs
        send("", DISCONNECT)
        exit()
