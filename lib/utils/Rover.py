import json
import random
import threading
import time
from utils.SDNNode import SDNNode


class Rover(SDNNode):
    """
    rover_id - id, host - host, port - port
    known_peers = host:port,host:port // For simulation purposes
    operation_area - 0,0,999,999 // Coordinates that defines the operation area. Second point always bigger
    speed - 20
    """
    def __init__(self, rover_id, host, port, known_peers, operation_area, max_speed, radio_range, peer_ids):
        self.operation_area = [
            [int(operation_area.split(',')[0]), int(operation_area.split(',')[1])],
            [int(operation_area.split(',')[2]), int(operation_area.split(',')[3])]
        ]
        super().__init__(rover_id, {
            'x': random.randint(self.operation_area[0][0], self.operation_area[1][0]),
            'y': random.randint(self.operation_area[0][1], self.operation_area[1][1])
        }, host, int(port), known_peers.split(',') if known_peers != '' else [], radio_range)

        # Sensors
        self.max_speed = max_speed
        self.speedometer = {'x': 0, 'y': 0}

        # Status
        self.movement_enabled = True
        self.low_battery_mode = False
        # self.is_leader = False
        self.is_election_going_on = False
        self.election_timing = 0.0
        self.leader = ''

        #Peer IDs
        self.peer_ids = peer_ids.split(',') if peer_ids != '' else []

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
                    # print('[INFO] Battery recharged. Low battery mode disabled', flush=True)
            elif random.randint(0, 100) < 5:
                # print('[INFO] Battery low. Deploying solar panels', flush=True)
                self.low_battery_mode = True
                self.networking_disabled = True

            if not self.low_battery_mode:
                turns_spent_recharging = 0
                if self.movement_enabled:
                    self._move()
                    # print('[INFO] Rover moved to new location', flush=True)
            else:
                # print('[INFO] Recharging...', flush=True)
                turns_spent_recharging += 1
            
            if(self.leader != self.node_id and self.is_election_going_on == False):
                self._start_election()
            print('[INFO] Current Leader is:',self.leader)
            time.sleep(20)

    def _handle_request(self, message, client_address):
        # print('[DEBU] Received message from', client_address[0] + ':' + str(client_address[1]) +
        #      ':', message, flush=True)
        content = json.loads(message['content'])

        if content['type'] == 'heartbeat':
           pass
        elif content['type'] == 'target' and content['nonce'] not in self.consumed_nonces.keys():
            self.consumed_nonces[content['nonce']] = time.time()
            if content['to'] == self.node_id:
                print('[INFO] That content was for me, so nice! Thank you', content['reply_to'])
            else:
                ttl = content['ttl'] - 1
                if ttl >= 0:
                    self.broadcast_message_to(content['message'], content['to'], content['reply_to'], content['nonce'], ttl)
        
        if content['type'] == 'target' and content['message'] == 'Election' and content['to']==self.node_id:
            print('[DEBUG] Available to be elected')
            self.is_election_going_on = True
            self.broadcast_message_to('Available', content['reply_to'], self.node_id) #Broadcast I am available to be elected
            self._start_election()
        
        if content['type'] == 'target' and content['message'] == 'Available' and content['to']==self.node_id:
            self.election_timing = 0
            print('[INFO] I am ',self.node_id,'.I lost the Election!! :(')
        
        if self.election_timing != 0 and self.election_timing+30 < time.time():
            self.broadcast(json.dumps({'type': 'election_winner','id':self.node_id})) #Broadcast I am a Leader
            self.leader = self.node_id
            self.is_election_going_on = False
        
        if content['type'] == 'election_winner':
            self.leader = content['id']
            self.is_election_going_on = False
            print('[DEBUG] I won election!!',content['id'])

    def start(self):
        threading.Thread(target=self._start_server).start()
        if self.node_id != 'network-visualizer':
            threading.Thread(target=self._start_engine).start()

    def _start_election(self):
        print('Starting Election!')
        own_id = self.node_id[-1]
        is_any = True
        for index, peer_id in enumerate(self.peer_ids):
            # print('[DEBUG]peer port for:', index, 'and id',peer_id,' is:',self.known_peers[index].split(':')[1])
            if peer_id[-1] <= own_id:
                is_any = False
                self.is_election_going_on = True
                print('Sending election message from:',self.node_id,'to:',peer_id)
                self.broadcast_message_to('Election', peer_id, self.node_id)
                self.election_timing = time.time() #Set the start time of election
        if(is_any):
            self.broadcast(json.dumps({'type': 'election_winner','id':self.node_id})) #Broadcast I am a Leader if there's no peer < self
            self.leader = self.node_id
            self.is_election_going_on = False
