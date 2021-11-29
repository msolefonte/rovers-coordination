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
            # and spends three turns in the same location.
            if self.low_battery_mode:
                if turns_spent_recharging >= 3:
                    self.low_battery_mode = False
                    self.networking_disabled = False
                    print('[INFO] Battery recharged. Low battery mode disabled', flush=True)
            elif random.randint(0, 100) < 5:
                print('[INFO] Battery low. Deploying solar panels', flush=True)
                self.low_battery_mode = True
                self.networking_disabled = True

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
        # TODO NOT TO EVERYONE BUT TO EVERYONE BIGGER THAN YOU
        self.broadcast({'type': 'election', 'emitter': self.node_id})

        time.sleep(30)

        if self.i_am_the_best_leader_available:
            print('[INFO] I won the election! Time to get corrupt')
            self.broadcast({'type': 'victory', 'emitter': self.node_id})
            self.leader_id = self.node_id
            self.is_election_going_on = False

    def _check_leadership(self):
        time.sleep(15)
        while True:
            time.sleep(random.randint(0, 60))
            if not self.low_battery_mode and not self.is_election_going_on:
                if not self.leader_id or self.leader_id != self.node_id or \
                        time.time() - self.known_rovers[self.leader_id] > 30:
                    try:
                        self._start_election()
                    except SystemError:
                        pass
                # if self.leader_id and self.leader_id == self.node_id:
                #     for rover in self.known_rovers.keys():
                #         if rover[-1] < self.node_id[-1] and time.time() - self.known_rovers[rover] > 30:
                #             try:
                #                 self._start_election()
                #                 break
                #             except SystemError:
                #                 pass

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
            elif content['type'] == 'targeted-heartbeat':
                self.known_rovers[content['reply_to']] = time.time()
                if content['to'] == self.node_id:
                    self._handle_election(content)
                else:
                    if ttl >= 0:
                        self.broadcast_message_to(content['message'], content['to'], content['reply_to'], content['nonce'],
                                                  ttl)
            elif content['type'] == 'election' or content['type'] == 'victory':
                self.known_rovers[content['emitter']] = time.time()
                if ttl >= 0:
                    self.broadcast({'type': content['type'], 'emitter': content['emitter']}, content['nonce'], ttl)
                self._handle_election(content)
        except SystemError:
            pass

    def _handle_election(self, content):
        if content['type'] == 'election':
            print('[DEBU] Election in process')
            self.is_election_going_on = True
            if self.node_id[-1] < content['emitter'][-1]:
                self.broadcast_message_to('election-reply', content['emitter'], self.node_id)
                self._start_election()

        if content['type'] == 'targeted_broadcast':
            if content['message'] == 'election-reply' and content['reply_to'][-1] < self.node_id[-1]:
                print('[DEBU] A bigger fish replied:', content['reply_to'])
                self.i_am_the_best_leader_available = False

        if content['type'] == 'victory':
            self.leader_id = content['emitter']
            self.is_election_going_on = False
            print('[INFO] Rover', content['emitter'], 'won election')

    def start(self):
        threading.Thread(target=self._start_server).start()
        threading.Thread(target=self._start_engine).start()
        threading.Thread(target=self._check_leadership).start()
