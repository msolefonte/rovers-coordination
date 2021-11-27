import sys
from Rover import Rover
from DataStorage import DataStorage
from time import sleep


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
                rover.broadcast_message_to('hello', 'rover5')
                rover.save_data('check',host)
        except SystemError:
            pass  # Networking disabled due to low battery in the rover


main()
