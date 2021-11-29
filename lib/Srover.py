import sys
from Rover import Rover
from time import sleep
from EarthStation import EarthStation


def main():
    print('[INFO] Rover started with args', sys.argv[1:], flush=True)
    rover_id, host, port, known_peers, coordinates, speed, radio_range = sys.argv[1:]
    rover = Rover(rover_id, host, int(port), known_peers, coordinates, int(speed), int(radio_range))
    rover.start()
    

    while True:
        sleep(5)
        try:
            rover.heartbeat()
            if rover_id == 'rover3':
                rover.broadcast_request('hello','rover5')
                rover.broadcast_request('hello_earth','earth-station')
                
        except SystemError:
            pass  # Networking disabled due to low battery in the rover


main()
