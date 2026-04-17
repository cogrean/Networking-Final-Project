import sys
import threading
import socket

LOCALIP = '0.0.0.0'
REMOTEIP = '128.146.189.120'
PORT = 6767
connections = []

clients = {}

local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# need to be able to reuse ports 

# bind servers object to the IP and Port nums
local_server.bind((LOCALIP, PORT))

local_server.settimeout(1.0)

local_server.listen()

print("local_server is listening on " + LOCALIP + ":" + str(PORT))

def handle_connection(conn, addr, username):
    while (True):
        try:
            
            message = conn.recv(1024).decode()
            if (message == "exit"): 
                del clients[username]
                # connections.remove((conn, addr))
                print(f"disconnecting from {str(addr)}")
                return
            
            if (message.startswith("@")):
                parts = message.split(' ', 1)
                
                if len(parts) >= 2:
                    target_user = parts[0][1:]
                    msg_text = parts[1]
                    
                    # If target username exists in the client dictionary 
                    if target_user in clients:
                        # Send the message only to that specific target client 
                        clients[target_user].send(f"[Private] {username}: {msg_text}".encode('utf-8'))
                    else:
                        # Inform the sender that the target user was not found 
                        conn.send(f"Server: User '{target_user}' not found.".encode('utf-8'))
                else:
                    # Inform the sender to use the correct format 
                    conn.send("Server: Invalid format. Use '@username message'".encode('utf-8'))
                    
            
            elif (message.startswith("Broadcast: ")):
                msg_text = message[11:]
                print(f"broadcasting '{msg_text}' from {username}")
                for user, c in clients.items():
                    if user != username:
                        # Add [Broadcast] and the sender's username so it's readable
                        c.send(f"[Broadcast] {username}: {msg_text}".encode('utf-8'))
        
        except:
            if username in clients:
                del clients[username]
            break
                
# def catch_connections(server):
#     while (True):
#         conn, addr = server.accept()
#         print(f"connecte to {addr}")
#         connections.append((conn, addr))
#         threading.Thread(target=handle_connection, daemon=True, args=(conn, addr)).start()
        
            
            
# accepts requests 
while (True):
    try:
        conn, addr = local_server.accept()
        print(f"connected to {addr}")
        
        conn.send(b"Server: Please enter your username:")
        username = conn.recv(1024).decode().strip()
        
        clients[username] = conn
        print(f"{addr} registered as '{username}'")
        
        # Start a new thread to handle communication with that client 
        threading.Thread(target=handle_connection, daemon=True, args=(conn, addr, username)).start()
    
    except socket.timeout:
        continue