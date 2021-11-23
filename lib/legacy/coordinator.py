import sys
from Coordinator import Coordinator


def main():
    print('[INFO] coordinator started with args', sys.argv[1:])
    host, port, coordinators = sys.argv[1:]

    coordinator = Coordinator(host, port, coordinators.split(',') if coordinators != '' else [])
    coordinator.start()


main()
