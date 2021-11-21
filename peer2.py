from lib.Peer import Peer
from time import sleep


# TODO TURN THIS INTO peer.py WITH BASH ARGS
def main():
    peer = Peer('node2', 'localhost', '9001', ['localhost:7000', 'localhost:7001', 'localhost:7002'])
    peer.start()

    while True:
        sleep(7)

        try:
            peer.send_message_to_peer('node1', 'Hello')
        except Exception as e:
            print('Not available :(', e)
            pass


main()
