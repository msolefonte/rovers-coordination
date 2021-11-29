import json
import socket
import threading
from time import sleep
import sys

def main():
    network_id = sys.argv[1:]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        soc.connect(('LAPTOP-C2621QF2', int(7101)))
        message = json.dumps({
                    'type': 'external',
                    'content': { 'test':'test-routing'},
                    'to': 'earth-station',
                    'from': 'external'
                })
        sleep(5) 
        soc.sendall(str.encode(message))

threading.Thread(target=main).start()        
    