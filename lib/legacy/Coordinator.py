"""
For each network we will have three coordinators with fixed ip/port. The coordinators will have a leader selected by
them. If they receive a read message, they will reply. If they receive a write message, they will just send the read to
the leader. The leader will write and expand the change to the others.

If one of the coordinator fails, new leader elected. When a node joins asks who is the leader and gets an updated list

UPDATE: No need for a leader because no need for strong consistency
"""

import json
import socket
import threading
import time
from utils.P2PNode import P2PNode


# TODO GIVE COORDINATORS SOME KIND OF USE, LIKE WHO HOLDS X RESOURCE
# TODO USE UUID TO IDENTIFY PEERS
class Coordinator(P2PNode):
    def __init__(self, host, port, coordinators):
        super().__init__(host, port, coordinators)

    def _handle_request(self, soc):
        connection, client_address = soc.accept()
        try:
            data = connection.recv(1024)
            if data:
                try:
                    request = json.loads(data.decode())

                    old_known_peers = json.dumps(self.known_peers)
                    if request['type'] == 'liveness':
                        print('[DEBU]', client_address, '/liveness', flush=True)
                        self.known_peers['peers'][request['id']] = {
                            'host': request['host'],
                            'port': request['port'],
                            'last-heartbeat': time.time()
                        }

                        if json.dumps(self.known_peers) != old_known_peers:
                            print('[DEBU] Known peers updated:', json.dumps(self.known_peers), flush=True)

                    elif request['type'] == 'get-peers':
                        print('[DEBU]', client_address, '/get-peers', flush=True)
                        connection.sendall(str.encode(json.dumps(self.known_peers)))
                except Exception as e:
                    print('[WARN] Error parsing request:', e, flush=True)
        finally:
            connection.close()

    def _start_server(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            while True:
                try:
                    soc.bind((self.host, self.port))
                    break
                except OSError:
                    print('[WARN] Address already in use. Waiting for it to be free.', flush=True)
                    time.sleep(5)
            soc.listen(1)

            while True:
                self._handle_request(soc)
        finally:
            soc.close()

    def start(self):
        threading.Thread(target=self._start_server).start()
        threading.Thread(target=self._update_known_peers).start()
        threading.Thread(target=self._delete_old_peers).start()
