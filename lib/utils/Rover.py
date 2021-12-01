import json
import random
import threading
import time
from .RoverEngine import RoverEngine
from .RoverRadio import RoverRadio
from .RoverSensors import RoverSensors
from .constants import SLEEP_TIME_BATTERY, SLEEP_TIME_ELECTION_FIRST, SLEEP_TIME_ELECTION_MAX, \
    SLEEP_TIME_ELECTION_MIN, SLEEP_TIME_ELECTION_RESULTS, SLEEP_TIME_HEARTBEAT


class Rover(RoverRadio, RoverEngine, RoverSensors):
    def __init__(self, rover_id, sdn_properties, physical_properties):
        # Deployment
        self.location = physical_properties['location']

        # Individual components
        RoverRadio.__init__(self, rover_id, sdn_properties, physical_properties)
        RoverEngine.__init__(self, physical_properties)
        RoverSensors.__init__(self)

        # Battery
        self.low_battery_mode = False
        self.turns_spent_recharging = 0

        # Coordination
        self.is_election_going_on = False
        self.i_am_the_best_leader_available = False
        self.known_rovers = {}  # {rover_id: timestamp}
        self.leader_id = None

    # Battery

    """
    The battery has a 5% probability of getting empty. Once empty, the rover enters in the low battery mode and spends 
    three turns in the same location, disables networking and, if it was, stops acting as a leader.
    """
    def _disable_capabilities(self):
        print('[INFO] Battery low. Deploying solar panels', flush=True)
        self.low_battery_mode, self.networking_disabled, self.movement_disabled = True, True, True
        if self.leader_id == self.node_id:
            self.leader_id = None

    def _enable_capabilities(self):
        self.low_battery_mode, self.networking_disabled, self.movement_disabled = False, False, False
        print('[INFO] Battery recharged. Low battery mode disabled', flush=True)

    def _check_battery(self):
        if self.low_battery_mode:
            if self.turns_spent_recharging >= 3:
                self._enable_capabilities()
                self.turns_spent_recharging = 0
            else:
                print('[INFO] Recharging...', flush=True)
                self. turns_spent_recharging += 1
        elif random.randint(0, 100) < 5:
            self._disable_capabilities()

    def _start_battery_check(self):
        while True:
            self._check_battery()
            time.sleep(SLEEP_TIME_BATTERY)

    # Heartbeat

    def _start_heartbeat(self):
        while True:
            self.heartbeat(noerr=True)
            time.sleep(SLEEP_TIME_HEARTBEAT)

    # Coordination

    def _wait_for_election_results(self):
        self.i_am_the_best_leader_available = True
        time.sleep(SLEEP_TIME_ELECTION_RESULTS)

        if self.i_am_the_best_leader_available:
            print('[INFO] I won the election! Time to get corrupt')
            self.broadcast({'type': 'victory', 'emitter': self.node_id}, noerr=True)
            self.leader_id = self.node_id
            self.is_election_going_on = False
        else:
            print('[DEBU] There are better candidates to win the election')

    def _start_election(self):
        print('[INFO] Leader election started')
        self.is_election_going_on = True

        self.election_start_time = time.time()
        self.broadcast({'type': 'election', 'emitter': self.node_id}, noerr=True)
        self._wait_for_election_results()

    def _check_leadership(self):
        time.sleep(SLEEP_TIME_ELECTION_FIRST)
        while True:
            time.sleep(random.randint(SLEEP_TIME_ELECTION_MIN, SLEEP_TIME_ELECTION_MAX))
            if not self.low_battery_mode and not self.is_election_going_on:
                if not self.leader_id or \
                        (self.leader_id != self.node_id and time.time() - self.known_rovers[self.leader_id] > 30):
                    self._start_election()

    # # Handle election in process

    def _handle_election_start(self, content):
        if content['type'] == 'election':
            print('[INFO] Election in process')
            self.is_election_going_on = True
            if self.node_id[-1] < content['emitter'][-1]:
                self.broadcast_message_to('election-reply', content['emitter'], self.node_id, noerr=True)
            for rover in list(self.known_rovers):
                if rover[-1] < self.node_id[-1]:
                    self.broadcast_message_to('election-propagation', rover, self.node_id, noerr=True)
            self._wait_for_election_results()

    def _handle_election_propagation(self, content):
        if content['type'] == 'targeted-broadcast':
            if content['message'] == 'election-propagation':
                self.broadcast_message_to('election-reply', content['reply_to'], self.node_id, noerr=True)
            if content['message'] == 'election-reply' and content['reply_to'][-1] < self.node_id[-1]:
                print('[DEBU] A bigger fish replied:', content['reply_to'])
                self.i_am_the_best_leader_available = False

    def _handle_election_victory(self, content):
        if content['type'] == 'victory':
            self.leader_id = content['emitter']
            self.is_election_going_on = False
            print('[INFO] Election done. Rover', content['emitter'], 'won')

    def _handle_election(self, content):
        self._handle_election_start(content)
        self._handle_election_propagation(content)
        self._handle_election_victory(content)

    def _handle_election_messages(self, content):
        if content['type'] == 'election' or content['type'] == 'victory':
            self.known_rovers[content['emitter']] = time.time()
            if content['ttl'] - 1 >= 0:
                self.broadcast({'type': content['type'], 'emitter': content['emitter']}, content['nonce'],
                               content['ttl'] - 1, True)
            self._handle_election(content)

    # Handle requests

    def _handle_heartbeat(self, content):
        if content['type'] == 'heartbeat':
            self.known_rovers[content['rover_id']] = time.time()
            if content['ttl'] - 1 >= 0:
                self.broadcast({'type': 'heartbeat', 'rover_id': content['rover_id']}, content['nonce'],
                               content['ttl'] - 1, True)

    def _handle_targeted_broadcast(self, content):
        if content['type'] == 'targeted-broadcast':
            self.known_rovers[content['reply_to']] = time.time()
            if content['to'] == self.node_id:
                self._handle_election(content)
            else:
                if content['ttl'] - 1 >= 0:
                    self.broadcast_message_to(content['message'], content['to'], content['reply_to'],
                                              content['nonce'], content['ttl'] - 1, noerr=True)

    def _handle_decrypted_request(self, message, _):
        content = json.loads(message['content'])

        if content['nonce'] not in self.consumed_nonces:
            self.consumed_nonces[content['nonce']] = time.time()
        else:
            return

        self._handle_heartbeat(content)
        self._handle_targeted_broadcast(content)
        self._handle_election_messages(content)

    def start(self):
        threading.Thread(target=self._start_server).start()
        threading.Thread(target=self._start_engine).start()
        threading.Thread(target=self._start_sensors).start()
        threading.Thread(target=self._start_heartbeat).start()
        threading.Thread(target=self._check_leadership).start()

    def am_i_leader(self):
        return self.leader_id == self.node_id
