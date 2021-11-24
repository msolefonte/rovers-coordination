import json
import socket
import time
import uuid


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
        self.low_battery_mode = False
        self.consumed_nonces = {}  # {nonce: timestamp}

    def _is_too_far_away(self, location):
        return ((((location['x'] - self.location['x'])**2) + ((location['y']-self.location['y'])**2))**0.5) > \
               self.radio_range

    def _handle_message(self, message, client_address, connection):
        raise NotImplementedError

    def _start_server(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            while True:
                try:
                    soc.bind((self.host, self.port))
                    print('[INFO] [SIM/TEST] Address bound.', flush=True)
                    break
                except OSError as e:
                    print('[WARN] [SIM/TEST] Address already in use. Waiting for it to be free.', flush=True)
                    time.sleep(5)

            soc.listen(1)
            while True:
                connection, client_address = soc.accept()
                try:
                    data = connection.recv(1024)
                    message = json.loads(data.decode())
                    if data:
                        # print('[TRAC] [SIM/TEST]', client_address, 'sent', message, flush=True)
                        # Simulates it is out of physical range. Basically refuses connection.
                        if self.low_battery_mode or \
                                (message['emitter'] != 'network-visualizer' and
                                 self._is_too_far_away(message['location'])):
                            connection.sendall('TOO_FAR_AWAY'.encode())
                        else:
                            self._handle_message(message, client_address, connection)
                finally:
                    connection.close()
        finally:
            soc.close()

    @staticmethod
    def _send_message_to_known_peer(host, port, message, tries=1):
        for i in range(tries):
            backoff = int((2 ** i)) - 1
            try:
                if i > 0 and backoff > 0:
                    # print('[DEBU] [SIM/TEST] Waiting', backoff, 'seconds before reconnecting', flush=True)
                    time.sleep(backoff)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
                    soc.connect((host, int(port)))
                    soc.sendall(str.encode(message))

                    data = soc.recv(1024).decode()
                    if data == 'TOO_FAR_AWAY':  # Simulates it is out of physical range. Assume connection refused.
                        raise ConnectionError('Connection refused by ', host + ':' + port)
                    return data
            except ConnectionError:
                pass
            except Exception as e:
                print('[WARN] [SIM/TEST] Error trying to reach', host + ':' + port + ':', e, flush=True)
        raise ConnectionError('Connection refused by ', host + ':' + port)

    # Simulates a wireless broadcast
    def broadcast(self, message):
        if not self.low_battery_mode:
            print('[INFO] Sending a broadcast message', flush=True)
            replies = []
            for peer in self.known_peers:
                try:
                    peer_ip, peer_port = peer.split(':')
                    reply = json.loads(self._send_message_to_known_peer(peer_ip, peer_port, json.dumps(
                        {'emitter': self.node_id, 'location': self.location, 'body': message}
                    )))
                    print('[INFO] Rover', reply['emitter'], 'at', str(reply['location']['x']) + ',' +
                          str(reply['location']['y']), 'replied:', reply['body'], flush=True)
                    replies.append(reply)
                except ConnectionError:
                    pass
                except Exception as e:
                    print('[ERRO] [SIM/TEST] Broadcast simulation error:', e, flush=True)

            if len(replies) == 0:
                print('[INFO] Nobody got the broadcast. Am I alone? I should\'ve stayed at home with Beth.', flush=True)

            return replies
        else:
            raise SystemError('Broadcasting disabled due to the rover being in low energy mode')

    def heartbeat(self):
        return self.broadcast(json.dumps({'type': 'heartbeat'}))

    # Simulates a wireless broadcast
    def send_message_to(self, message, target_id, reply_to_id=None, nonce=None, ttl=16):
        if not self.low_battery_mode:
            nonce = nonce if nonce else uuid.uuid4().hex
            reply_to_id = reply_to_id if reply_to_id else self.node_id

            print('[INFO] Broadcasting message targeting', target_id + '. (Origin', reply_to_id + ')')

            self.broadcast(json.dumps({
                'type': 'target',
                'message': message,
                'to': target_id,
                'reply_to': reply_to_id if reply_to_id else self.node_id,
                'nonce': nonce,
                'ttl': ttl
            }))

            self.consumed_nonces[nonce] = time.time()
        else:
            raise SystemError('Broadcasting disabled due to the rover being in low energy mode')
