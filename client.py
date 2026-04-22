import socket 

HOST_IP = '128.146.189.120'
PORT = 1234

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((HOST_IP, PORT))

client.sendall(b"Hello, From client!")

data = client.recv(1024) 
print("received: ", data.decode())

client.close()