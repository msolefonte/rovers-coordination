import socket
import threading
import time
from utils.SDNNode import SDNNode
import json

class EarthStation(SDNNode):

    storage_location = r'C:\Restricted\study\DataScience\TCD\Scalable computing\Project3\GITHUBNew\sc-p3\lib\DataStorage.txt'

    def __init__(self, node_id, host, port, peers):
        self.node_id = node_id
        self.host = host
        self.port = int(port)
        self.networking_disabled = False
        self.known_peers = peers.split(',')
        self.location = 'Earth'
         
    def find_port(self,node_id):
        peer_no = int(node_id[5])
        peer_port = 7001
        for i in range(len(self.known_peers)):
            if i == peer_no:
                peer_port = self.known_peers[i][16:]
        return str(peer_port)

    def storing_routing_data(self):
        while True:
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soc.bind((self.host, self.port))
            soc.listen(1)
            connection, client_address = soc.accept()
            data = connection.recv(1024)
            data_key, data_value = SDNNode.decrypt_message(data,SDNNode.private_key,SDNNode.private_iv)
            if data_key == SDNNode.private_network_key:
                print(data_value)
                with open(EarthStation.storage_location, 'a', encoding='utf-8') as f:
                    f.write(data_value)
            else :
                leader = 'rover5'
                #leader_port = '7004'
                leader_port = EarthStation.find_port(self,leader)
                print('leader port:' + leader_port)
                data_value = data.decode()
                #data_value = json.loads(data.decode())
                print('[INFO] Sending external network message to rovers ')
                print(data_value)
                message = json.dumps({
                'type': 'target',
                'message': data_value,
                'to': leader,
                'reply_to': 'Earth' ,
                'nonce': None,
                'ttl': 16
            })
                self._send_message_to_known_peer_no_error(self.host, leader_port, message)
                
            connection.close()
            soc.close()
            


    def start(self):
        threading.Thread(target=self.storing_routing_data).start()
        #threading.Thread(target=self.routing_external_networks).start()
        
