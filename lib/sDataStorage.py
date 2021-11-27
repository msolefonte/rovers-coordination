import sys
from DataStorage import DataStorage


def main():
    print('[INFO] DataStorage started running')
    node_id, host, port = sys.argv[1:]

    data_storage = DataStorage(node_id, host, int(port))
    data_storage.start()


main()
