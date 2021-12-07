import sys
from random import randint
from lib.Rover import Rover


def parse_arguments():
    print('[INFO] Rover started with args', sys.argv[1:], flush=True)
    rover_id, host, port, known_peers, coordinates, max_speed, radio_range, encryption_key = sys.argv[1:]

    area = [[int(coordinates.split(',')[0]), int(coordinates.split(',')[1])],
            [int(coordinates.split(',')[2]), int(coordinates.split(',')[3])]]

    sdn_properties = {
        'host': host,
        'port': int(port),
        'known_peers': known_peers.split(',') if known_peers != '' else []
    }
    physical_properties = {
        'operation_area': area,
        'location': {'x': randint(area[0][0], area[1][0]), 'y': randint(area[0][1], area[1][1])},
        'max_speed': int(max_speed),
        'radio_range': int(radio_range),
        'encryption_key': encryption_key
    }

    return rover_id, sdn_properties, physical_properties


def main():
    rover = Rover(*parse_arguments())
    rover.start()


main()
