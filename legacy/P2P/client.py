import socket

HOST = 'localhost'
PORT = 34000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Text Here!')
    data = s.recv(1024)

print('Received',repr(data))
