import socket 

HOST_IP = '127.0.0.1'
PORT = 1234

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST_IP, PORT))

client.sendall(b"Hello, From client!")

data = client.recv(1024) 
print("received: ", data.decode())

client.close()