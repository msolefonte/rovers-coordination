import sys
from utils.Rover import Rover
from time import sleep


def main():
    print('[INFO] Rover started with args ', sys.argv[1:], flush=True)
    rover_id, host, port, known_peers, coordinates, speed, radio_range, peer_ids = sys.argv[1:]
    rover = Rover(rover_id, host, int(port), known_peers, coordinates, int(speed), int(radio_range), peer_ids)
    rover.start()

    while True:
        sleep(5)
        try:
            rover.heartbeat()
            if rover_id == 'rover8':
                rover.broadcast_message_to('hello', 'rover0')
        except SystemError:
            pass  # Networking disabled due to low battery in the rover


main()
