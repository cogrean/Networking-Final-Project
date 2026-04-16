import socket

HOST_IP = '0.0.0.0'
PORT = 6767

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind server object to the IP and Port num
server.bind((HOST_IP, PORT))

server.listen()

print("server is listening on " + HOST_IP + ":" + str(PORT))

# accepts requests 
conn, addr = server.accept()
print(f"connected by {addr}")

# receive and print data
data = conn.recv(1024)
print("received: ", data.decode())

conn.sendall(b"Hello From server!")

conn.close()

server.close()

# 