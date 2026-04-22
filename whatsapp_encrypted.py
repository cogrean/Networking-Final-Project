import socket 
import sys
import threading
import os
from crypto_utils import SecureMessenger
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

# localhost will connect using local server IP (0.0.0.0)
LOCALHOST = '127.0.0.1'
REMOTEHOST = '128.146.189.120'
SERVER_PORT = 6767

def server_connect():
    local_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    
    try:
        local_client.settimeout(5)
        local_client.connect((LOCALHOST, SERVER_PORT))
        local_client.settimeout(None)
        return local_client
    except Exception as e:
        print("failed to connect locally, attempting over-the-air server connection...")
        
    remote_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    
    try: 
        remote_client.settimeout(5)
        remote_client.connect((REMOTEHOST, SERVER_PORT))
        remote_client.settimeout(None)
        return remote_client
    except Exception as e:
        print("failed to connect over the air, error: ", str(e))
        return None
        
def establish_secure_connection(client_socket):
    # Receive senders RSA public key
    public_pem = client_socket.recv(1024)
    server_public_key = serialization.load_pem_public_key(public_pem)

    # Generate AES key
    shared_key = os.urandom(32)

    # Encrypt AES key using RSA key
    encrypted_aes_key = server_public_key.encrypt(
        shared_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    client_socket.send(encrypted_aes_key)
    return SecureMessenger(shared_key)

def broadcast_client_handler():
    
    print("attempting to connect to server")
    client = server_connect()
    
    if client is None:
        print("\nunable to connect to server, ensure server is on and remote IP is correct\n\nreturning to menu")
        return
    
    messenger = establish_secure_connection(client)
    
    print("Secure connection established. Please enter your username:")
    username = input()
    client.send(messenger.encrypt(username))
    
    print(f"\nWelcome {username}! You are in Secure Broadcast Mode.")

    print("\nListening for broadcast... enter messages to broadcast (type 'exit' to exit)\n")
    
    def receive_messages(client, stop_signal, messenger):
        while not stop_signal.is_set():
            data = client.recv(1024)
            print(f"Decrypted message: {messenger.decrypt(data)}")
                        
    def send_messages(client):
        while (True):
            user_in = input()
            
            if (user_in == "exit"):
                print("Exiting broadcast mode, returning to menu")    
                client.send(messenger.encrypt("exit"))
                return
            
            client.send(messenger.encrypt(f"Broadcast: {user_in}"))
            print()
            
    stop_signal = threading.Event()
    
    threading.Thread(target=receive_messages, daemon=True, args=(client, stop_signal, messenger)).start()
        
    send_messages(client)
    
    stop_signal.set()
            
def one_on_one_client_handler():
    print("attempting to connect to server...")
    client = server_connect()
    
    if client is None:
        print("\nunable to connect to server, ensure server is on.\nreturning to menu")
        return
        
    messenger = establish_secure_connection(client)

    # Wait for the server to request a username 
    # server_prompt = client.recv(1024).decode()
    # print(server_prompt)
    
    # Send username to server
    username = input("Secure connection established, enter your username: ")
    client.send(messenger.encrypt(username))
    
    print(f"\nWelcome {username}! You are in One-on-One Chat.")
    print("To send a private message, type in the format: @username message ")
    print("Type 'exit' to return to menu\n")
    
    stop_signal = threading.Event()
    
    def receive_messages(client, stop_signal, messenger):
        while not stop_signal.is_set():
            try:
                data = client.recv(1024)
                if data:
                    print(messenger.decrypt(data))
            except:
                break
                
    # Background thread to listen for messages
    threading.Thread(target=receive_messages, daemon=True, args=(client, stop_signal, messenger)).start()
        
    def send_messages(client):
        while True:
            user_in = input()
            
            if user_in == "exit":
                print("Exiting One-on-One mode, returning to menu")    
                client.send(messenger.encrypt("exit"))
                return
            
            # Ensure right format
            if not user_in.startswith("@"):
                print("Error: Please use the format '@username message'")
                continue
                
            # Send message to server
            client.send(messenger.encrypt(user_in))
            
    send_messages(client)
    stop_signal.set()       
        
while (True):
    print("\n[1] Broadcast\n[2] One-on-One\n[3] Exit")
    
    mode = input()
    
    try:
        mode = int(mode.strip())
    except Exception as e:
        mode = None
        
    if mode not in  {1, 2, 3}:
        continue
    
    match mode:
        case 1:
            broadcast_client_handler()
        case 2:
            one_on_one_client_handler()
        case 3:
            print("\nSee ya!")
            sys.exit(0)
        case _:
            continue
            
    
