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
        self.election_start_time = 0.0
        self.is_election_going_on = False
        self.known_rovers = []
        self.leader_id = ''

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
            
            if(self.leader_id != self.node_id and self.is_election_going_on == False):
                self._start_election()
            print('[INFO] Current Leader is:',self.leader_id)
            time.sleep(20)

    def _handle_decrypted_request(self, message, client_address):
        # print('[DEBU] Received message from', client_address[0] + ':' + str(client_address[1]) +
        #      ':', message, flush=True)
        content = json.loads(message['content'])
        emitter = message['emitter']

        if content['type'] == 'heartbeat' and emitter[-1] not in self.known_rovers:
            self.known_rovers.append(emitter[-1])
        elif content['type'] == 'target' and content['nonce'] not in self.consumed_nonces.keys():
            self.consumed_nonces[content['nonce']] = time.time()
            if content['to'] == self.node_id:
                print('[INFO] That content was for me, so nice! Thank you', content['reply_to'])
            else:
                ttl = content['ttl'] - 1
                if ttl >= 0:
        self._handle_election(message)

    def _handle_election(self, message):
        content = json.loads(message['content'])
    
        if content['type'] == 'target' and content['message'] == 'election' and content['to']==self.node_id:
            print('[DEBU] Election in process. Reporting availability to be elected')
            self.is_election_going_on = True
            self.broadcast_message_to('available', content['reply_to'], self.node_id)  # Broadcast I am available to be elected
            self._start_election()
        
        if content['type'] == 'target' and content['message'] == 'available' and content['to']==self.node_id:
            self.election_start_time = 0
            print('[DEBU] Leader election lost.')
        
        if self.election_start_time != 0 and self.election_start_time+30 < time.time():
            self.broadcast(json.dumps({'type': 'election_winner','id':self.node_id}))  # Broadcast I am a Leader
            self.leader_id = self.node_id
            self.is_election_going_on = False
        
        if content['type'] == 'election_winner':
            self.leader_id = content['id']
            self.is_election_going_on = False
            print('[INFO] I won election!')

    def start(self):
        threading.Thread(target=self._start_server).start()
        if self.node_id != 'network-visualizer':
            threading.Thread(target=self._start_engine).start()

    def _start_election(self):
        print('[INFO] Leader election started')
        own_id = self.node_id[-1]
        i_am_the_best_leader_available = True
        self.is_election_going_on = True
            
        self.election_start_time = time.time()
        for index, rover_id in enumerate(self.known_rovers):
            if rover_id <= own_id:
                i_am_the_best_leader_available = False
                print('[DEBU] Sending election message to:', rover_id)
                self.broadcast_message_to('election', rover_id, self.node_id)
        if i_am_the_best_leader_available:
            self.broadcast(json.dumps({'type': 'election_winner', 'id':self.node_id}))
            self.leader_id = self.node_id
            self.is_election_going_on = False
