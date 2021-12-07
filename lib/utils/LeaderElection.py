import random
import time
from utils.constants import SLEEP_TIME_ELECTION_FIRST, SLEEP_TIME_ELECTION_MAX, \
    SLEEP_TIME_ELECTION_MIN, SLEEP_TIME_ELECTION_RESULTS


class LeaderElection:
    @staticmethod
    def _wait_for_election_results(rover: 'Rover'):
        rover.i_am_the_best_leader_available = True
        time.sleep(SLEEP_TIME_ELECTION_RESULTS)

        if rover.i_am_the_best_leader_available:
            print('[INFO] I won the election! Time to get corrupt')
            rover.broadcast({'type': 'victory', 'emitter': rover.node_id}, noerr=True)
            rover.leader_id = rover.node_id
            rover.is_election_going_on = False
        else:
            print('[DEBU] There are better candidates to win the election')

    @staticmethod
    def _rebroadcast_election(rover: 'Rover'):
        for known_rover in list(rover.known_rovers):
            if known_rover[-1] < rover.node_id[-1]:
                rover.broadcast_message_to('election-propagation', known_rover, rover.node_id, noerr=True)

    @staticmethod
    def _handle_election_start(rover: 'Rover', content):
        if content['type'] == 'election':
            print('[INFO] Election in process')
            rover.is_election_going_on = True
            if rover.node_id[-1] < content['emitter'][-1]:
                rover.broadcast_message_to('election-reply', content['emitter'], rover.node_id, noerr=True)
            LeaderElection._rebroadcast_election(rover)
            LeaderElection._wait_for_election_results(rover)

    @staticmethod
    def _handle_election_propagation(rover: 'Rover', content):
        if content['message'] == 'election-propagation':
            rover.broadcast_message_to('election-reply', content['reply_to'], rover.node_id, noerr=True)

    @staticmethod
    def _handle_election_reply(rover: 'Rover', content):
        if content['message'] == 'election-reply' and content['reply_to'][-1] < rover.node_id[-1]:
            print('[DEBU] A bigger fish replied:', content['reply_to'])
            rover.i_am_the_best_leader_available = False

    @staticmethod
    def _handle_election_targeted(rover: 'Rover', content):
        if content['type'] == 'targeted-broadcast':
            LeaderElection._handle_election_propagation(rover, content)
            LeaderElection._handle_election_reply(rover, content)

    @staticmethod
    def _handle_election_victory(rover: 'Rover', content):
        if content['type'] == 'victory':
            rover.leader_id = content['emitter']
            rover.is_election_going_on = False
            print('[INFO] Election done. Rover', content['emitter'], 'won')

    @staticmethod
    def handle_election(rover: 'Rover', content):
        LeaderElection._handle_election_start(rover, content)
        LeaderElection._handle_election_targeted(rover, content)
        LeaderElection._handle_election_victory(rover, content)

    @staticmethod
    def _start_election(rover: 'Rover'):
        print('[INFO] Leader election started')
        rover.is_election_going_on = True

        rover.election_start_time = time.time()
        rover.broadcast({'type': 'election', 'emitter': rover.node_id}, noerr=True)
        LeaderElection._wait_for_election_results(rover)

    @staticmethod
    def _is_leader_down(rover: 'Rover'):
        return not rover.leader_id or \
               (rover.leader_id != rover.node_id and time.time() - rover.known_rovers[rover.leader_id] > 30)

    @staticmethod
    def _check_leadership(rover: 'Rover'):
        time.sleep(random.randint(SLEEP_TIME_ELECTION_MIN, SLEEP_TIME_ELECTION_MAX))
        if not rover.low_battery_mode and not rover.is_election_going_on:
            if LeaderElection._is_leader_down(rover):
                LeaderElection._start_election(rover)

    @staticmethod
    def check_leadership(rover: 'Rover'):
        time.sleep(SLEEP_TIME_ELECTION_FIRST)
        while True:
            LeaderElection._check_leadership(rover)
