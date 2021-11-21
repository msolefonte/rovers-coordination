import socket

HOST = 'localhost'
PORT = 34000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
conn, addr = s.accept()
while True:
    data = conn.recv(1024)
    if not data:
        print('Closing..')
        break
    conn.sendall(b'Request served')
