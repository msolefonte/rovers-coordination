import sys
from Rover import Rover
from time import sleep


def main():
    print('[INFO] Rover started with args', sys.argv[1:], flush=True)
    rover_id, host, port, known_peers, coordinates, speed, radio_range = sys.argv[1:]
    rover = Rover(rover_id, host, port, known_peers, coordinates, speed, radio_range)
    rover.start()

    while True:
        sleep(20)
        rover.broadcast('Hello')


main()
