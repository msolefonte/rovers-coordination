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
        try:
            replies = rover.broadcast('Hello')

            # Tracker node does not really interact with the network. It is there just to print the map.
            if rover_id == 'network-visualizer':
                mars_map = [['x'] * 15 for x in range(15)]
                for reply in replies:
                    mars_map[int(reply['location']['x']/200)][int(reply['location']['y']/200)] = reply['emitter'][-1]

                map_string = ''
                for line in mars_map:
                    map_string += ' '.join(line) + '\n'
                print(map_string[:-1], flush=True)
        except SystemError:
            pass


main()
