"""
When a node joins the network, it will contact any of the coordinators randomly to report it is available. It can be
reported every x time. After reporting, ask for the the map of directions and download it (storing it in memory). When
trying to communicate to other node, it will use the map in memory. If not reachable or node not in map, will download
again.

If reachable, standard p2p connection between the two nodes. Peers have to be able to continue even if coordinators are
down, but joining the network will be impossible
"""

import json
import socket
import socketserver
import random
import threading


# TODO ADD LOGIC
class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print(self.request)
        print(self.request.recv(1024))
        data = self.request.recv(1024).strhost()
        print(self.client_address)
        print(data.decode())

        self.request.sendall('world'.encode())


class Peer:
    def __init__(self, host, port, coordinators):
        self.host = host
        self.port = int(port)
        self.coordinators = coordinators

        self.known_peers = {}
        self.server = None

    # TODO ADD LOGIC
    def _get_known_peers_from_coordinator(self, host, port):
        raise NotImplementedError

    # TODO ADD LOGIC
    def _report_liveness_to_coordinator(self, host, port):
        self.send_message_to_known_peer(host, port, json.dumps({'type': 'liveness'}))
        print(str.encode(json.dumps({'type': 'liveness'})))

    def _update_known_peers(self):
        if len(self.coordinators) > 0:
            starting_point = random.randint(0, len(self.coordinators) - 1)

            for i in range(len(self.coordinators)):
                coord_host, coord_port = self.coordinators[(starting_point + i) % len(self.coordinators)].split(':')
                try:
                    self._get_known_peers_from_coordinator(coord_host, coord_port)
                    break
                except Exception as e:
                    print('[WARN] Coordinator', coord_host, coord_port, 'down or not reachable:', e)
    
    def _report_liveness(self):
        if len(self.coordinators) > 0:
            starting_point = random.randint(0, len(self.coordinators) - 1)

            for i in range(len(self.coordinators)):
                coord_host, coord_port = self.coordinators[(starting_point + i) % len(self.coordinators)].split(':')
                try:
                    self._report_liveness_to_coordinator(coord_host, coord_port)
                    break
                except Exception as e:
                    print('[WARN] Coordinator', coord_host, coord_port, 'down or not reachable:', e)
                    
    def _start_server(self):
        with socketserver.TCPServer((self.host, self.port), TCPHandler) as server:
            server.serve_forever()

    # TODO ADD LOGIC
    # TODO ADD RECONNECTION
    @staticmethod
    def send_message_to_known_peer(host, port, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
                soc.connect((host, int(port)))
                soc.sendall(str.encode(message))
                data = soc.recv(1024)
                print(data.decode())
        except Exception as e:
            raise e

    def start(self):
        self._update_known_peers()
        self.server = threading.Thread(target=self._start_server).start()
        self._report_liveness()

    # TODO RAISE A REAL ERROR
    def send_message_to_peer(self, peer_id, message):
        if peer_id not in self.known_peers:
            self._update_known_peers()

        if peer_id not in self.known_peers:
            raise NotImplementedError

        self.send_message_to_known_peer(
            self.known_peers[peer_id]['host'],
            self.known_peers[peer_id]['port'],
            message
        )
