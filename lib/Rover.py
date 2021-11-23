import json
import random
import socket
import threading
import time
import uuid


class Rover:
    """
    rover_id - id, host - host, port - port
    known_peers = host:port,host:port // For simulation purposes
    operation_area - 0,0,999,999 // Coordinates that defines the operation area. Second point always bigger
    speed - 20
    """
    def __init__(self, rover_id, host, port, known_peers, operation_area, max_speed, radio_range):
        self.rover_id = rover_id

        # Network - Used to run the simulation. Not representative of the real topology
        self.host = host
        self.port = int(port)
        self.known_peers = known_peers.split(',') if known_peers != '' else []

        # Physical capabilities
        self.operation_area = [
            [int(operation_area.split(',')[0]), int(operation_area.split(',')[1])],
            [int(operation_area.split(',')[2]), int(operation_area.split(',')[3])]
        ]
        self.max_speed = int(max_speed)
        self.radio_range = int(radio_range)

        # Sensors
        self.location = {
            'x': random.randint(self.operation_area[0][0], self.operation_area[1][0]),
            'y': random.randint(self.operation_area[0][1], self.operation_area[1][1])
        }
        self.speedometer = {'x': 0, 'y': 0}

        # Status
        self.movement_enabled = True
        self.low_battery_mode = False
        self.consumed_nonces = {}  # {nonce: timestamp}

    def _move(self):
        x_movement = random.randint(0, self.max_speed) * (1 if random.random() < 0.5 else -1)
        y_movement = random.randint(0, self.max_speed) * (1 if random.random() < 0.5 else -1)

        if self.location['x'] + x_movement < self.operation_area[0][0]:
            x_movement = self.operation_area[0][0] - self.location['x']
        if self.location['x'] + x_movement > self.operation_area[1][0]:
            x_movement = self.operation_area[1][0] - self.location['x']
        if self.location['y'] + y_movement < self.operation_area[0][1]:
            y_movement = self.operation_area[0][1] - self.location['y']
        if self.location['y'] + y_movement > self.operation_area[1][1]:
            y_movement = self.operation_area[1][1] - self.location['y']

        self.location = {'x': self.location['x'] + x_movement, 'y': self.location['y'] + y_movement}
        self.speedometer = {'x': x_movement, 'y': y_movement}

    def _start_engine(self):
        turns_spent_recharging = 0
        while True:
            # The battery has a 5% probability of getting empty. Once empty, the rover enters in the low battery mode
            # and spends three turns in the same location.
            if self.low_battery_mode:
                if turns_spent_recharging >= 3:
                    self.low_battery_mode = False
                    print('[INFO] Battery recharged. Low battery mode disabled', flush=True)
            elif random.randint(0, 100) < 5:
                print('[INFO] Battery low. Deploying solar panels', flush=True)
                self.low_battery_mode = True

            if not self.low_battery_mode:
                turns_spent_recharging = 0
                if self.movement_enabled:
                    self._move()
                    print('[INFO] Rover moved to new location', flush=True)
                    print('[DEBU] Positioning System lecture:', self.location, flush=True)
                    print('[DEBU] Speedometer lecture:', self.speedometer, flush=True)
            else:
                print('[INFO] Recharging...', flush=True)
                turns_spent_recharging += 1
            time.sleep(30)

    def _is_too_far_away(self, location):
        return ((((location['x'] - self.location['x'])**2) + ((location['y']-self.location['y'])**2))**0.5) > \
               self.radio_range

    def _handle_message(self, message, connection):
        if message['type'] == 'heartbeat':
            connection.sendall(json.dumps(
                {'emitter': self.rover_id, 'location': self.location, 'body': 'OK'}
            ).encode())
        elif message['type'] == 'target' and message['nonce'] not in self.consumed_nonces.keys():
            self.consumed_nonces[message['nonce']] = time.time()
            if message['to'] == self.rover_id:
                print('[INFO] That message was for me, so nice! Thank you', message['reply_to'])
            else:
                ttl = message['ttl'] - 1
                if ttl >= 0:
                    self.send_message_to_rover(message['message'], message['to'], message['reply_to'],
                                               message['nonce'], ttl)

    def _start_server(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            while True:
                try:
                    soc.bind((self.host, self.port))
                    break
                except OSError as e:
                    print('[WARN] [SIM/TEST] Address already in use. Waiting for it to be free:', e, flush=True)
                    time.sleep(5)

            soc.listen(1)
            while True:
                connection, client_address = soc.accept()
                try:
                    data = connection.recv(1024)
                    message = json.loads(data.decode())
                    if data:
                        # print('[INFO] [SIM/TEST]', client_address, 'sent', message, flush=True)
                        # Simulates it is out of physical range. Basically refuses connection.
                        if self.low_battery_mode or \
                                (message['emitter'] != 'network-visualizer' and
                                 self._is_too_far_away(message['location'])):
                            connection.sendall('TOO_FAR_AWAY'.encode())
                        else:
                            print('[DEBU] Received message from ', client_address[0] + ':' + str(client_address[1]) +
                                  ':', message, flush=True)
                            self._handle_message(json.loads(message['body']), connection)
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
                        {'emitter': self.rover_id, 'location': self.location, 'body': message}
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
    def send_message_to_rover(self, message, rover_id, reply_to_id=None, nonce=None, ttl=16):
        if not self.low_battery_mode:
            nonce = nonce if nonce else uuid.uuid4().hex
            reply_to_id = reply_to_id if reply_to_id else self.rover_id

            print('[INFO] Broadcasting message targeting', rover_id + '. (Origin', reply_to_id + ')')

            self.broadcast(json.dumps({
                'type': 'target',
                'message': message,
                'to': rover_id,
                'reply_to': reply_to_id if reply_to_id else self.rover_id,
                'nonce': nonce,
                'ttl': ttl
            }))

            self.consumed_nonces[nonce] = time.time()
        else:
            raise SystemError('Broadcasting disabled due to the rover being in low energy mode')

    def start(self):
        threading.Thread(target=self._start_server).start()
        if self.rover_id != 'network-visualizer':
            threading.Thread(target=self._start_engine).start()
