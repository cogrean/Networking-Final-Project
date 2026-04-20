import sys
import threading
import socket
from crypto_utils import SecureMessenger, decrypt_key_with_rsa
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

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

# set up rsa keys
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

def handle_connection(conn, addr, username):
    user_messenger = clients[username]["messenger"]
    while (True):
        try:
            ciphertext = conn.recv(1024)
            print(f"Encrypted message: {ciphertext.hex()}")
            message = user_messenger.decrypt(ciphertext)
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
                    
                    if target_user in clients:
                        # Send message to only target
                        target_conn = clients[target_user]["conn"]
                        target_messenger = clients[target_user]["messenger"]

                        # Encrypt for the targets key
                        final_msg = f"[Private] {username}: {msg_text}"
                        target_conn.send(target_messenger.encrypt(final_msg))
                    else:
                        # No user
                        conn.send(user_messenger.encrypt(f"Server: User '{target_user}' not found."))
                else:
                    conn.send(user_messenger.encrypt("Server: Invalid format. Use '@username message'"))
                    
            
            elif (message.startswith("Broadcast: ")):
                msg_text = message[11:]
                print(f"broadcasting '{msg_text}' from {username}")

                for user, c in clients.items():
                    if user != username:
                        # Add [Broadcast] and the sender's username so it's readable
                        c["conn"].send(c["messenger"].encrypt(f"[Broadcast] {username}: {msg_text}"))
        
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
        
        # send RSA public key
        conn.send(public_pem)
        # receive and decrypt AES key
        encrypted_aes_key = conn.recv(256)
        shared_key = decrypt_key_with_rsa(private_key, encrypted_aes_key)
        messenger = SecureMessenger(shared_key)
        
        # receive encrypted username
        encrypted_username = conn.recv(1024)
        username = messenger.decrypt(encrypted_username).strip()

        clients[username] = {"conn": conn, "messenger": messenger}
        print(f"{addr} registered as '{username}'")
        
        threading.Thread(target=handle_connection, daemon=True, args=(conn, addr, username)).start()
    
    except socket.timeout:
        continue