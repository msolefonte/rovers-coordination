import json
import random
import threading
import time
from utils.SDNNode import SDNNode
from Sensors import Sensors

class Rover(SDNNode):
    """
    rover_id - id, host - host, port - port
    known_peers = host:port,host:port // For simulation purposes
    operation_area - 0,0,999,999 // Coordinates that defines the operation area. Second point always bigger
    speed - 20
    """
    def __init__(self, rover_id, host, port, known_peers, operation_area, max_speed, radio_range):
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
        self.sensors = Sensors()
        
        # Status
        self.movement_enabled = True
        self.low_battery_mode = False

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
                    # print('[DEBU] Positioning System lecture:', self.location, flush=True)
                    # print('[DEBU] Speedometer lecture:', self.speedometer, flush=True)
            else:
                print('[INFO] Recharging...', flush=True)
                turns_spent_recharging += 1
            time.sleep(30)

    def _handle_request(self, message, client_address):
        # print('[DEBU] Received message from', client_address[0] + ':' + str(client_address[1]) +
        #      ':', message, flush=True)
        
        content = json.loads(message['content'])
        if content['type'] == 'heartbeat':
            pass  # Good to know I guess. Maybe useful for something
        elif content['type'] == 'target' and content['nonce'] not in self.consumed_nonces.keys():
            self.consumed_nonces[content['nonce']] = time.time()
            if content['to'] == self.node_id:
                print('[INFO] That content was for me, so nice! Thank you', content['reply_to'])
            else:
                ttl = content['ttl'] - 1
                if ttl >= 0:
                    self.broadcast_message_to(content['message'], content['to'], content['reply_to'], content['nonce'], ttl)

    def start(self):
        threading.Thread(target=self._start_server).start()
        threading.Thread(target=self.sensors.update()).start()
        if self.node_id != 'network-visualizer':
            threading.Thread(target=self._start_engine).start()
