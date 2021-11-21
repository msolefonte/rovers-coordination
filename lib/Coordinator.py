"""
For each network we will have three coordinators with fixed ip/port. The coordinators will have a leader selected by
them. If they receive a read message, they will reply. If they receive a write message, they will just send the read to
the leader. The leader will write and expand the change to the others.

If one of the coordinator fails, new leader elected. When a node joins asks who is the leader and gets an updated list
"""

import json
import socket
import time


# TODO ADD LOGIC FOR COORDINATION / LEADER ELECTION
# TODO ADD A SMALL CLEANUP. KINDA UGLY
class Coordinator:
    def __init__(self, host, port, coordinators):
        self.host = host
        self.port = int(port)
        self.coordinators = coordinators

        self.leader_ip = None
        self.known_peers = {}

    def _start_server(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            while True:
                try:
                    soc.bind((self.host, self.port))
                    break
                except OSError:
                    print('[WARN] Address already in use. Waiting for it to be free.')
                    time.sleep(5)
            soc.listen(1)

            while True:
                connection, client_address = soc.accept()
                try:
                    data = connection.recv(1024)
                    if data:
                        try:
                            request = json.loads(data.decode())

                            old_known_peers = json.dumps(self.known_peers)
                            if request['type'] == 'liveness':
                                print('[DEBU]', client_address, '/liveness')
                                self.known_peers[request['id']] = {
                                    'host': request['host'],
                                    'port': request['port']
                                }

                                if json.dumps(self.known_peers) != old_known_peers:
                                    print('[DBU] Known peers updated:', json.dumps(self.known_peers))

                            elif request['type'] == 'get-peers':
                                print('[DEBU]', client_address, '/get-peers')
                                connection.sendall(str.encode(json.dumps(self.known_peers)))
                        except Exception as e:
                            print('[WARN] Error parsing request:', e)
                finally:
                    connection.close()
        finally:
            soc.close()

    def start(self):
        self._start_server()
