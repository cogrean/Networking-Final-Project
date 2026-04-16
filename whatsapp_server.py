import sys
import threading
import socket

LOCALIP = '0.0.0.0'
REMOTEIP = '172.27.51.40'
PORT = 6767
connections = []

local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# need to be able to reuse ports 

# bind servers object to the IP and Port nums
local_server.bind((LOCALIP, PORT))


local_server.listen()

print("local_server is listening on " + LOCALIP + ":" + str(PORT))

def handle_connection(conn, addr):
    while (True):
        message = conn.recv(1024).decode()
        if (message == "exit"): 
            connections.remove((conn, addr))
            print(f"disconnecting from {str(addr)}")
            return
        if (message.startswith("Broadcast: ")):
            print(f"broadcasting '{message[11:]}'")
            for c, a in connections:
                if (a == addr):
                    continue
                c.send(message[11:].encode('utf-8'))
                
# def catch_connections(server):
#     while (True):
#         conn, addr = server.accept()
#         print(f"connecte to {addr}")
#         connections.append((conn, addr))
#         threading.Thread(target=handle_connection, daemon=True, args=(conn, addr)).start()
        
            
            
# accepts requests 
while (True):
    conn, addr = local_server.accept()
    print(f"connected to {addr}")
    connections.append((conn, addr))
    
    threading.Thread(target=handle_connection, daemon=True, args=(conn, addr)).start()