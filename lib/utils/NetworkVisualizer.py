import threading
import time
from .RoverRadio import RoverRadio


class NetworkVisualizer(RoverRadio):
    def __init__(self, node_id, host, port, location_x, location_y, encryption_key):
        super().__init__(node_id, {'x': int(location_x), 'y': int(location_y)}, host, int(port), [], 999999999999,
                         encryption_key)

        self.rover_locations = {}

    def _handle_decrypted_request(self, message, client_address):
        print('[DEBU] Received message from', client_address[0] + ':' + str(client_address[1]) +
              ':', message, flush=True)
        self.rover_locations[message['emitter']] = message['location']

    # Assumes map of 3000x3000 in chunks of 125x125
    def _print_map(self):
        while True:
            time.sleep(30)
            mars_map = [['x'] * 24 for _ in range(24)]
            for rover in self.rover_locations:
                mars_map[int(self.rover_locations[rover]['x'] / 125)][int(self.rover_locations[rover]['y'] / 125)] = \
                    rover[-1]

            map_string = '--' * 23 + '\n'
            for line in mars_map:
                map_string += ' '.join(line) + '\n'
            print(map_string[:-1], flush=True)

    def start(self):
        threading.Thread(target=self._start_server).start()
        threading.Thread(target=self._print_map).start()
