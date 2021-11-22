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
import random
import threading
import time


# TODO IMPLEMENT GET KNOWN PEERS FROM CLOSE PEERS
# TODO ADD PERIODICAL GET KNOWN PEERS
class Peer:
    def __init__(self, peer_id, host, port, coordinators):
        self.id = peer_id
        self.host = host
        self.port = int(port)
        self.coordinators = coordinators

        self.known_peers = {}

    def _get_known_peers_from_coordinator(self, host, port):
        new_peers = json.loads(self.send_message_to_known_peer(host, port, json.dumps({
            'type': 'get-peers'
        })))

        old_known_peers = json.dumps(self.known_peers)

        for peer in new_peers:
            self.known_peers[peer] = new_peers[peer]

        if json.dumps(self.known_peers) != old_known_peers:
            print('[INFO] Known peers updated')
            print('[DEBU]', json.dumps(self.known_peers))

    def _report_liveness_to_coordinator(self, host, port):
        self.send_message_to_known_peer(host, port, json.dumps({
            'type': 'liveness',
            'id': self.id,
            'host': self.host,
            'port': self.port
        }))

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
        while True:
            print('[DEBU] Reporting liveness')
            if len(self.coordinators) > 0:
                starting_point = random.randint(0, len(self.coordinators) - 1)

                for i in range(len(self.coordinators)):
                    coord_host, coord_port = self.coordinators[(starting_point + i) % len(self.coordinators)].split(':')
                    try:
                        self._report_liveness_to_coordinator(coord_host, coord_port)
                        print('[DEBU] Liveness reported to coordinator', coord_host, coord_port)
                        break
                    except Exception as e:
                        print('[WARN] Coordinator', coord_host, coord_port, 'down or not reachable:', e)
            time.sleep(30)
                    
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
                        print(client_address, 'sent', data.decode())
                finally:
                    connection.close()
        finally:
            soc.close()

    # TODO ADD RECONNECTION
    @staticmethod
    def send_message_to_known_peer(host, port, message, tries=3, interval=None):
        backoff = interval

        for i in range(tries):
            if not interval:
                backoff = 2 ** i

            try:
                time.sleep(backoff)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
                    soc.connect((host, int(port)))
                    soc.sendall(str.encode(message))
                    data = soc.recv(1024)
                    return data.decode()
            except Exception as e:
                print('[WARN] Error trying to reach', host, port, ':', e)
                time.sleep(5)

    def start(self):
        self._update_known_peers()
        threading.Thread(target=self._start_server).start()
        threading.Thread(target=self._report_liveness).start()

    def send_message_to_peer(self, peer_id, message, tries=3, interval=None):
        if peer_id not in self.known_peers:
            self._update_known_peers()

        if peer_id not in self.known_peers:
            raise ConnectionError('Peer', peer_id, 'not known')

        self.send_message_to_known_peer(
            self.known_peers[peer_id]['host'],
            self.known_peers[peer_id]['port'],
            message, tries, interval
        )
