import socket 
import sys
import threading

# localhost will connect using local server IP (0.0.0.0)
LOCALHOST = '127.0.0.2'
REMOTEHOST = '172.27.51.40'
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
        
    

def broadcast_client_handler():
    
    print("attempting to connect to server")
    client = server_connect()
    
    if client is None:
        print("\nunable to connect to server, ensure server is on and remote IP is correct\n\nreturning to menu")
        return
    
    print("\nListening for broadcast... enter messages to broadcast (type 'exit' to exit)\n")
    
    def receive_messages(client, stop_signal):
        while not stop_signal.is_set():
            data = client.recv(1024) 
            print(data.decode())
                        
    def send_messages(client):
        while (True):
            user_in = input()
            
            if (user_in == "exit"):
                print("Exiting broadcast mode, returning to menu")    
                client.send(b"exit")
                return
            
            client.send((f"Broadcast: {user_in}").encode('utf-8'))
            print()
            
    stop_signal = threading.Event()
    
    threading.Thread(target=receive_messages, daemon=True, args=(client, stop_signal)).start()
        
    send_messages(client)
    
    stop_signal.set()
            
        
        
while (True):
    print("\n[1] Broadcast\n[2] One-on-One\n[3] Third Feature\n[4] Exit")
    
    mode = input()
    
    try:
        mode = int(mode.strip())
    except Exception as e:
        mode = None
        
    if mode not in  {1, 2, 3, 4}:
        continue
    
    match mode:
        case 1:
            broadcast_client_handler()
        case 2:
            # TODO: one-on-one
            continue
        case 3:
            # TODO: AI feature
            continue
        case 4:
            print("\nSee ya!")
            sys.exit(0)
        case _:
            continue
            
    
