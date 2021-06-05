Brendan Tschuy
June 2021

Request for Comments: 59449401

Internet Relay Chat Final Project Protocol

STATUS OF THIS MEMO

This draft is submitted only for use in CS594.001, Spring 2021.

ABSTRACT

Describing a basic IRC client, server, and protocol that can be
used with a single server and multiple clients.

1. INTRODUCTION
	1.1 Servers
	1.2 Clients
	1.3 Channels
2. PROTOCOL
	2.1 Overview
	2.2 Opcodes
	2.3 Messages
3. USAGE
	3.1 Overview

1. Introduction
1.1 Servers

The IRC server is hosted on 127.0.0.1 and accepts any 
connections made over socket on port 5432. The server
stays open indefinitely until the process is ended,
upon which it broadcasts a disconnect message to all
attached clients. When a server receives a message from
clients, it determines the operation to be executed
and can respond to one or many clients.

1.2 Clients

The IRC clients connect to the server on 127.0.0.1:5432.
The clients stay open until the user disconnects. One client
disconnecting will still allow other clients to stay
connected.

1.3 Channels

Channels, or rooms, allow clients to communicate with one
another in chat groups that other clients don't have
access to. Clients can leave and join rooms through chat
commands. Rooms will be deleted upon server exit.

2. PROTOCOL
2.1 Overview

Each message consists of between two and four parts:

[HEADER][OPCODE][MESSAGE]

or in some cases:

[HEADER][OPCODE][ARGUMENT][MESSAGE]

The header and opcode are always fixed width, so the server
knows to accept a fixed number of bytes for each section. The 
header size is set at 64 bytes and contains an integer 
corresponding with the number of bytes contained in the remainder
of the message. 

The opcode is 4 bytes and contains a string corresponding with
a command. Having 4 bytes provides ample space for future opcodes.

Some commands, like private messaging touched upon in section 
<>, require an optional argument, such as the name of the user
to which one wishes to send a private message.

Finally, the message itself typically makes up the bulk of the 
message's size. So long as the message corresponds with the 
length provided in the header, and is below the maximum message
size of 2048 bytes, it can be safely transmitted by the server.

2.2 Opcodes

All commands are prefixed with '!'.

2.2.1 Server-Client Communication
The following opcodes are provided:

0001 JOIN_SERVER 
0002 SEND_MESSAGE
0003 JOIN_ROOM
0004 NAME_CHANGE
0005 DISCONNECT
0006 CREATE_ROOM
0007 SEND_TO_ROOM
0008 LEAVE_ROOM
0009 PRIVATE_MESSAGE
0010 LIST_ROOMS
0011 LIST_MEMBERS
0012 LIST_ONLINE
2.2.2 Client-side Opcodes
The opcode '!help' can be used to display all available codes.

2.2.2.2 
2.3 Messages

2.2.2.1 JOIN_SERVER: used upon server join to set desired
username

2.2.2.2 SEND_MESSAGE: default opcode, or used to send a message
globally

2.2.2.3 JOIN_ROOM usage: !join <roomName>
Used to join an existing room

2.2.2.4 NAME_CHANGE usage: !namechange <desiredName>
Changes name to target name

2.2.2.5 DISCONNECT usage: !dc
Disconnects gracefully from server

2.2.2.6 CREATE_ROOM usage: !create <roomName>
Creates new room and joins it

2.2.2.7 SEND_TO_ROOM usage: !room <roomName> <message>
Sends message to roomName, if it exists

2.2.2.8 PRIVATE_MESSAGE usage: !pm <userName> <message>
Sends message to userName, if they are online

2.2.2.9 LIST_ROOMS usage: !rooms
Lists all open rooms

2.2.2.10 LIST_MEMBERS usage: !members <roomName>
Lists all online members in roomName

2.2.2.11 LIST_ONLINE usage: !online
Lists all online users globally

2.4 Other Messages

2.4.1 Server Disconnect
If the server disconnects, it sends 'XXXX' and the clients know
to gracefully disconnect as well. It is not possible for
clients to send a false flag 'XXXX' to willingly crash the server.

3. USAGE
3.1 The server can be started with the following command:

python3 server.py

No further instruction is necessary.

The client can be started with the following command:

python3 client.py

One can now type a username, then use commands as listed above,
or use '!help' for a reminder, before communicating with other
clients or otherwise using the server.
