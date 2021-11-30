import json
import socket
import time
import threading


class SDNNode:
    def __init__(self, node_id, location, host, port, known_peers, radio_range):
        # Identification
        self.node_id = node_id

        # Capabilities
        self.radio_range = radio_range

        # Network
        self.host = host
        self.port = port
        self.known_peers = known_peers

        # Status
        self.location = location
        self.networking_disabled = False

    # Simulation

    def _is_too_far_away(self, location):
        return ((((location['x'] - self.location['x'])**2) + ((location['y']-self.location['y'])**2))**0.5) > \
               self.radio_range

    @staticmethod
    def _send_message_to_known_peer(host, port, message, tries):
        for i in range(tries):
            backoff = int((2 ** i)) - 1
            try:
                if i > 0 and backoff > 0:
                    time.sleep(backoff)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
                    soc.connect((host, int(port)))
                    soc.sendall(str.encode(message))

                    data = soc.recv(1024).decode()
                    if data == 'TOO_FAR_AWAY':  # Simulates it is out of physical range. Assume connection refused.
                        raise ConnectionError('Connection refused by ', host + ':' + port)
            except ConnectionError:
                pass
            except Exception as e:
                print('[WARN] [SDN] Error trying to reach', host + ':' + port + ':', e, flush=True)
        raise ConnectionError('Connection refused by ', host + ':' + port)

    def _send_message_to_known_peer_no_error(self, host, port, message, tries=3):
        try:
            SDNNode._send_message_to_known_peer(host, port, json.dumps(
                {'emitter': self.node_id, 'location': self.location, 'content': message}
            ), tries)
        except ConnectionError:
            pass
        except Exception as e:
            print('[ERRO] [SDN] Broadcast simulation error:', e, flush=True)

    def _start_server(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            while True:
                try:
                    soc.bind((self.host, self.port))
                    print('[INFO] [SDN] Address bound.', flush=True)
                    break
                except OSError as e:
                    print('[WARN] [SDN] Address already in use. Waiting for it to be free.', flush=True)
                    time.sleep(5)

            soc.listen(1)
            while True:
                connection = None
                try:
                    connection, client_address = soc.accept()
                    data = connection.recv(1024)
                    message = json.loads(data.decode())
                    if data:
                        # Simulates it is out of physical range. Basically refuses connection.
                        if self.networking_disabled or self._is_too_far_away(message['location']):
                            connection.sendall('TOO_FAR_AWAY'.encode())
                        else:
                            threading.Thread(
                                target=lambda: self._handle_request(message, client_address)).start()
                except Exception as e:
                    print('[WARN] [SDN] Error listening:', e)
                finally:
                    if connection:
                        connection.close()
        finally:
            soc.close()

    # Simulated methods

    def _handle_request(self, message, client_address):
        raise NotImplementedError

    def broadcast(self, message):
        if not self.networking_disabled:
            for peer in self.known_peers:
                peer_ip, peer_port = peer.split(':')
                threading.Thread(
                    target=lambda: self._send_message_to_known_peer_no_error(peer_ip, peer_port, message)
                ).start()
        else:
            raise SystemError('Broadcasting disabled')
