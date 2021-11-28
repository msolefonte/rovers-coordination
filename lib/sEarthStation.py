import sys
from EarthStation import EarthStation


def main():
    print('[INFO] Earth Station started running')
    node_id, host, port, peers = sys.argv[1:]

    data_storage = EarthStation(node_id, host, int(port),peers)
    data_storage.start()


main()
