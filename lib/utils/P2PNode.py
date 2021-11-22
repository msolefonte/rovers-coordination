import json
import random
import socket
import time


class P2PNode:
    def __init__(self, host, port, coordinators):
        self.host = host
        self.port = int(port)
        self.known_peers = {'peers': {}, 'coordinators': coordinators}

    # TODO ADD SOME KIND OF TIMESTAMP REGARDING LAST UPDATE
    # TODO MAYBE REMOVE NODES IF TIMESTAMP IS TO OLD
    def _get_known_peers_from_coordinator(self, host, port):
        new_peers = json.loads(self.send_message_to_known_peer(host, port, json.dumps({
            'type': 'get-peers'
        })))

        old_known_peers = json.dumps(self.known_peers)

        for peer in new_peers['peers']:
            self.known_peers['peers'][peer] = new_peers['peers'][peer]

        for coordinator in new_peers['coordinators']:
            if coordinator not in self.known_peers['coordinators']:
                self.known_peers['coordinators'].append(coordinator)

        if json.dumps(self.known_peers) != old_known_peers:
            print('[INFO] Known peers updated', flush=True)
            print('[DEBU]', json.dumps(self.known_peers), flush=True)

    def _update_known_peers(self):
        coordinators = self.known_peers['coordinators']
        if len(coordinators) > 0:
            starting_point = random.randint(0, len(coordinators) - 1)

            for i in range(len(coordinators)):
                coord_host, coord_port = coordinators[(starting_point + i) % len(coordinators)].split(':')
                try:
                    self._get_known_peers_from_coordinator(coord_host, coord_port)
                    break
                except Exception as e:
                    print('[WARN] Coordinator', coord_host, coord_port, 'down or not reachable:', e, flush=True)

    @staticmethod
    def send_message_to_known_peer(host, port, message, tries=3, interval=None):
        backoff = interval

        for i in range(tries):
            if not interval:
                backoff = int((2 ** i)) - 1

            try:
                if i > 0 and backoff > 0:
                    print('[DEBU] Waiting', backoff, 'seconds before reconnecting', flush=True)
                    time.sleep(backoff)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
                    soc.connect((host, int(port)))
                    soc.sendall(str.encode(message))
                    data = soc.recv(1024)
                    return data.decode()
            except Exception as e:
                print('[WARN] Error trying to reach', host, port, ':', e, flush=True)
                time.sleep(5)

        # TODO REMOVE AFTER SOME TIME FROM KNOWN (?)
        raise ConnectionError('Connection refused by ', host, port)
