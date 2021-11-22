import json
import socket
import random
import threading
import time
from utils.P2PNode import P2PNode


# TODO ASK OTHER PEERS FOR SPECIFIC IDS, WITH TTL
# TODO IMPLEMENT GET KNOWN PEERS FROM CLOSE PEERS
# TODO ADD PERIODICAL GET KNOWN PEERS
class Peer(P2PNode):
    def __init__(self, peer_id, host, port, coordinators):
        super().__init__(host, port, coordinators)
        self.id = peer_id

    def _report_liveness_to_coordinator(self, host, port):
        self.send_message_to_known_peer(host, port, json.dumps({
            'type': 'liveness',
            'id': self.id,
            'host': self.host,
            'port': self.port
        }))

    # TODO USE TIMESTAMPS WITH LIVENESS
    def _report_liveness(self):
        coordinators = self.known_peers['coordinators']
        while True:
            print('[DEBU] Reporting liveness', flush=True)
            if len(coordinators) > 0:
                starting_point = random.randint(0, len(coordinators) - 1)

                for i in range(len(coordinators)):
                    coord_host, coord_port = coordinators[(starting_point + i) % len(coordinators)].split(':')
                    try:
                        self._report_liveness_to_coordinator(coord_host, coord_port)
                        print('[DEBU] Liveness reported to coordinator', coord_host, coord_port, flush=True)
                        break
                    except Exception as e:
                        print('[WARN] Coordinator', coord_host, coord_port, 'down or not reachable:', e, flush=True)
            time.sleep(30)
                    
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
                connection, client_address = soc.accept()
                try:
                    data = connection.recv(1024)
                    if data:
                        print('[INFO]', client_address, 'sent', data.decode(), flush=True)
                finally:
                    connection.close()
        finally:
            soc.close()

    def start(self):
        self._update_known_peers()
        threading.Thread(target=self._start_server).start()
        threading.Thread(target=self._report_liveness).start()

    def send_message_to_peer(self, peer_id, message, tries=3, interval=None):
        if peer_id not in self.known_peers['peers']:
            self._update_known_peers()

        if peer_id not in self.known_peers['peers']:
            raise ConnectionError('Peer', peer_id, 'not known')

        self.send_message_to_known_peer(
            self.known_peers['peers'][peer_id]['host'],
            self.known_peers['peers'][peer_id]['port'],
            message, tries, interval
        )
