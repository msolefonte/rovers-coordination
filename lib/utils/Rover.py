import json
import random
import threading
import time
from .RoverRadio import RoverRadio


class Rover(RoverRadio):
    """
    rover_id - id, host - host, port - port
    known_peers = host:port,host:port // For simulation purposes
    operation_area - 0,0,999,999 // Coordinates that defines the operation area. Second point always bigger
    speed - 20
    """
    def __init__(self, rover_id, host, port, known_peers, operation_area, max_speed, radio_range, encryption_key):
        self.operation_area = [
            [int(operation_area.split(',')[0]), int(operation_area.split(',')[1])],
            [int(operation_area.split(',')[2]), int(operation_area.split(',')[3])]
        ]
        super().__init__(rover_id, {
            'x': random.randint(self.operation_area[0][0], self.operation_area[1][0]),
            'y': random.randint(self.operation_area[0][1], self.operation_area[1][1])
        }, host, int(port), known_peers.split(',') if known_peers != '' else [], radio_range, encryption_key)

        # Sensors
        self.max_speed = max_speed
        self.speedometer = {'x': 0, 'y': 0}

        # Status
        self.movement_enabled = True
        self.low_battery_mode = False

        # Coordination
        self.is_election_going_on = False
        self.i_am_the_best_leader_available = False
        self.known_rovers = {}
        self.leader_id = None

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
            # and spends three turns in the same location, disables networking and, if it was, stops acting as a leader.
            if self.low_battery_mode:
                if turns_spent_recharging >= 3:
                    self.low_battery_mode = False
                    self.networking_disabled = False
                    print('[INFO] Battery recharged. Low battery mode disabled', flush=True)
            elif random.randint(0, 100) < 5:
                print('[INFO] Battery low. Deploying solar panels', flush=True)
                self.low_battery_mode = True
                self.networking_disabled = True
                if self.leader_id == self.node_id:
                    self.leader_id = None

            if not self.low_battery_mode:
                turns_spent_recharging = 0
                if self.movement_enabled:
                    self._move()
                    print('[INFO] Rover moved to new location', flush=True)
            else:
                print('[INFO] Recharging...', flush=True)
                turns_spent_recharging += 1
            time.sleep(20)

    def _start_election(self):
        print('[INFO] Leader election started')
        self.i_am_the_best_leader_available = True
        self.is_election_going_on = True

        self.election_start_time = time.time()
        self.broadcast({'type': 'election', 'emitter': self.node_id})
        self._wait_for_election_results()

    def _wait_for_election_results(self):
        time.sleep(30)

        if self.i_am_the_best_leader_available:
            print('[INFO] I won the election! Time to get corrupt')
            self.broadcast({'type': 'victory', 'emitter': self.node_id})
            self.leader_id = self.node_id
            self.is_election_going_on = False

    def _check_leadership(self):
        time.sleep(60)
        while True:
            time.sleep(random.randint(30, 90))
            if not self.low_battery_mode and not self.is_election_going_on:
                if not self.leader_id or \
                        (self.leader_id != self.node_id and time.time() - self.known_rovers[self.leader_id] > 30):
                    try:
                        self._start_election()
                    except SystemError:
                        pass

    def _handle_decrypted_request(self, message, _):
        try:
            content = json.loads(message['content'])
            ttl = content['ttl'] - 1

            if content['nonce'] not in self.consumed_nonces:
                self.consumed_nonces[content['nonce']] = time.time()
            else:
                return

            if content['type'] == 'heartbeat':
                self.known_rovers[content['rover_id']] = time.time()
                if ttl >= 0:
                    self.broadcast({'type': 'heartbeat', 'rover_id': content['rover_id']}, content['nonce'], ttl)
            elif content['type'] == 'targeted-broadcast':
                self.known_rovers[content['reply_to']] = time.time()
                if content['to'] == self.node_id:
                    self._handle_election(content)
                else:
                    if ttl >= 0:
                        self.broadcast_message_to(content['message'], content['to'], content['reply_to'],
                                                  content['nonce'], ttl)
            elif content['type'] == 'election' or content['type'] == 'victory':
                self.known_rovers[content['emitter']] = time.time()
                if ttl >= 0:
                    self.broadcast({'type': content['type'], 'emitter': content['emitter']}, content['nonce'], ttl)
                self._handle_election(content)
        except SystemError:
            pass

    def _handle_election(self, content):
        if content['type'] == 'election':
            print('[INFO] Election in process')
            self.is_election_going_on = True
            if self.node_id[-1] < content['emitter'][-1]:
                self.broadcast_message_to('election-reply', content['emitter'], self.node_id)
            for rover in list(self.known_rovers):
                if rover[-1] < self.node_id[-1]:
                    self.broadcast_message_to('election-propagation', rover, self.node_id)
            self._wait_for_election_results()

        elif content['type'] == 'targeted-broadcast':
            if content['message'] == 'election-propagation':
                self.broadcast_message_to('election-reply', content['reply_to'], self.node_id)
            if content['message'] == 'election-reply' and content['reply_to'][-1] < self.node_id[-1]:
                print('[DEBU] A bigger fish replied:', content['reply_to'])
                self.i_am_the_best_leader_available = False

        elif content['type'] == 'victory':
            self.leader_id = content['emitter']
            self.is_election_going_on = False
            print('[INFO] Election done. Rover', content['emitter'], 'won')

    def start(self):
        threading.Thread(target=self._start_server).start()
        threading.Thread(target=self._start_engine).start()
        threading.Thread(target=self._check_leadership).start()
