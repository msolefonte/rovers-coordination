import sys
from time import sleep
from utils.Rover import Rover


def main():
    print('[INFO] Rover started with args', sys.argv[1:], flush=True)
    rover_id, host, port, known_peers, coordinates, speed, radio_range, encryption_key = sys.argv[1:]
    rover = Rover(rover_id, host, int(port), known_peers, coordinates, int(speed), int(radio_range), encryption_key)
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
