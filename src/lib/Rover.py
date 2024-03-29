import json
import threading
import time
from lib.components.RoverAntenna import RoverAntenna
from lib.components.RoverBattery import RoverBattery
from lib.components.RoverEngine import RoverEngine
from lib.components.RoverRadio import RoverRadio
from lib.components.RoverSensors import RoverSensors
from lib.utils.LeaderElection import LeaderElection


class Rover(RoverAntenna, RoverBattery, RoverEngine, RoverRadio, RoverSensors):
    def __init__(self, rover_id, sdn_properties, physical_properties):
        # Deployment
        self.location = physical_properties['location']

        # Coordination
        self.is_election_going_on = False
        self.i_am_the_best_leader_available = False
        self.known_rovers = {}  # {rover_id: timestamp}
        self.leader_id = None

        # Individual components - Respect start order
        RoverRadio.__init__(self, rover_id, sdn_properties, physical_properties)
        RoverEngine.__init__(self, physical_properties)
        RoverAntenna.__init__(self)
        RoverBattery.__init__(self)
        RoverSensors.__init__(self)

    # Handle requests

    def _handle_heartbeat(self, content):
        self.known_rovers[content['rover_id']] = time.time()
        if content['ttl'] - 1 >= 0:
            self.broadcast({'type': 'heartbeat', 'rover_id': content['rover_id']}, content['nonce'],
                           content['ttl'] - 1, True)

    def _handle_targeted_broadcast(self, content):
        self.known_rovers[content['reply_to']] = time.time()
        if content['to'] == self.node_id:
            LeaderElection.handle_election(self, content)
        elif content['ttl'] - 1 >= 0:
            self.broadcast_message_to(content['message'], content['to'], content['reply_to'], content['nonce'],
                                      content['ttl'] - 1, noerr=True)

    def _handle_election_messages(self, content):
        self.known_rovers[content['emitter']] = time.time()
        if content['ttl'] - 1 >= 0:
            self.broadcast({'type': content['type'], 'emitter': content['emitter']}, content['nonce'],
                            content['ttl'] - 1, True)
        LeaderElection.handle_election(self, content)

    def _nonce_already_consumed(self, nonce):
        if nonce not in self.consumed_nonces:
            self.consumed_nonces[nonce] = time.time()
            return False
        return True

    def _handle_decrypted_request(self, message, _):
        content = json.loads(message['content'])

        if not self._nonce_already_consumed(content['nonce']):
            if content['type'] == 'heartbeat':
                self._handle_heartbeat(content)
            elif content['type'] == 'targeted-broadcast':
                self._handle_targeted_broadcast(content)
            elif content['type'] == 'election' or content['type'] == 'victory':
                self._handle_election_messages(content)

    def start(self):
        threading.Thread(target=self._start_server).start()
        threading.Thread(target=self._start_engine).start()
        threading.Thread(target=self._start_sensors).start()
        threading.Thread(target=self._start_battery_check).start()
        threading.Thread(target=self._start_heartbeat).start()
        threading.Thread(target=lambda: LeaderElection.check_leadership(self)).start()

    def am_i_leader(self):
        return self.leader_id == self.node_id
