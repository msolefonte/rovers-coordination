import sys
from time import sleep
from utils.Rover import Rover


def main():
    print('[INFO] Rover started with args', sys.argv[1:], flush=True)
    rover_id, host, port, known_peers, coordinates, speed, radio_range, encryption_key = sys.argv[1:]
    rover = Rover(rover_id, host, int(port), known_peers.split(',') if known_peers != '' else [], [
        [int(coordinates.split(',')[0]), int(coordinates.split(',')[1])],
        [int(coordinates.split(',')[2]), int(coordinates.split(',')[3])]
    ], int(speed), int(radio_range), encryption_key)
    rover.start()


main()
