from lib.Peer import Peer
from time import sleep


def main():
    peer = Peer('localhost', '9000', ['localhost:7000', 'localhost:7001', 'localhost:7002'])
    peer.start()

    while True:
        sleep(5)

        try:
            peer.send_message_to_known_peer('localhost', '9001', 'Hello')
        except Exception as e:
            print('Not available :(', e)
            pass


main()
