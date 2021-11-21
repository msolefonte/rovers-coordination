"""
For each network we will have three coordinators with fixed ip/port. The coordinators will have a leader selected by
them. If they receive a read message, they will reply. If they receive a write message, they will just send the read to
the leader. The leader will write and expand the change to the others.

If one of the coordinator fails, new leader elected. When a node joins asks who is the leader and gets an updated list
"""

import json
import socketserver
import threading


# TODO ADD LOGIC


class Coordinator:
    class _TCPHandler(socketserver.BaseRequestHandler):
        def handle(self):
            data = self.request.recv(1024)
            if json.loads(data.decode())['type'] == 'liveness':
                # TODO But Hooooow
                print('Now I should add to known hosts', self.client_address[0], self.client_address[1])

            self.request.sendall('coord'.encode())

    def __init__(self, host, port, coordinators):
        self.host = host
        self.port = int(port)
        self.coordinators = coordinators

        self.leader_ip = None
        self.known_hosts = {}
        self.server = None

    def _start_server(self):
        with socketserver.TCPServer((self.host, self.port), Coordinator._TCPHandler) as server:
            server.serve_forever()

    def start(self):
        self.server = threading.Thread(target=self._start_server).start()
