import sys
from Peer import Peer
from time import sleep


def main():
    print('[INFO] peer started with args', sys.argv[1:])
    peer_id, host, port, coordinators, targets = sys.argv[1:]
    peer = Peer(peer_id, host, port, coordinators.split(',') if coordinators != '' else [])
    peer.start()

    while True:
        for target in targets.split(','):
            sleep(5)
            try:
                peer.send_message_to_peer(target, 'Hello')
            except Exception as e:
                print('[ERRO] Peer', target, 'not reachable:', e)


main()
