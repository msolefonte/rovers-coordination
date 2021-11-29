import socket
import threading
import json
import os
from utils.SDNNode import SDNNode
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class EarthStation(SDNNode):

    directory = './'
    filename = "DataStorage.txt"
    storage_location = os.path.join(directory, filename)
    #storage_location = r'C:\Restricted\study\DataScience\TCD\Scalable computing\Project3\GITHUBNew\sc-p3\lib\DataStorage.txt'
    leader = 'rover8'

    private_key = 856 #Manu
    private_iv = 154  #Manu
    private_network_key = 'rover_pwd'
    public_network_key =  'earthcall'

     # Encryption and Decryption of messags for security
    def encrypt_message(msg,keynum,ivnum,earth_comm=False):
        backend = default_backend()
        key = keynum.to_bytes(16,'big')
        iv = ivnum.to_bytes(16,'big')
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()
        padded_msg = str.encode(msg+(16-(len(msg)%16))*' ')
        ct = encryptor.update(padded_msg) + encryptor.finalize()
        if earth_comm ==False:
            #ct=str.encode(SDNNode.private_network_key+ct.hex())
            ct=EarthStation.private_network_key+ct.hex()
        else:
            ct=EarthStation.public_network_key+ct.hex()
        return ct


    def decrypt_message(self,ct,keynum,ivnum):
        backend = default_backend()
        try:
            key = keynum.to_bytes(16,'big')
            iv = ivnum.to_bytes(16,'big')
        except Exception as e:
            print('[WARN] [SDN] Invalid key provided by rover', e, flush=True)
        try:
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
            decryptor = cipher.decryptor()
            #st= ct.decode()
            st = ct
            ct_key = st[:9]
            ct_value = ''
            msg =''
            msg_decoded= ''
            if (ct_key == EarthStation.private_network_key) or (ct_key == EarthStation.public_network_key):
                ct_value = bytes.fromhex(st[9:])
                msg = decryptor.update(ct_value) + decryptor.finalize()
                msg_decoded = str(msg,'utf-8').rstrip()
            else:
                msg_decoded =st
                #print('[WARN] [SDN] Unautorized message, ignoring the message:'+st)
        except Exception as e:
            print('[WARN] [SDN] Invalid encryptions (possible injections), ignoring the message', e, flush=True)    
        return ct_key , msg_decoded

    def __init__(self, node_id, host, port, peers):
        self.node_id = node_id
        self.host = host
        self.port = int(port)
        self.networking_disabled = False
        self.known_peers = peers.split(',')
        self.location = 'Earth'
        self.consumed_nonces = {}
         
    

    def is_json(myjson):
        try:
            json.loads(myjson)
        except ValueError as e:
            return False
        return True

    def broadcast_request_earth(self,message,target,sender):
        message_encrypted = EarthStation.encrypt_message(message,EarthStation.private_key,EarthStation.private_iv)
        self.broadcast_message_to(message_encrypted,target,sender)

    def storing_routing_data(self):
        while True:
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soc.bind((self.host, self.port))
            soc.listen(1)
            connection, client_address = soc.accept()
            data = connection.recv(1024)
            message = json.loads(data.decode())
            content = json.loads(message['content']) if EarthStation.is_json(message['content']) else False
            #print(content)
            if content and ('type' in content)  and content['type'] == 'target' and ('to' in content) and content['to'] == self.node_id :
                content_key,content_decrypted = EarthStation.decrypt_message(self,content['message'],EarthStation.private_key,EarthStation.private_iv)
                if content_key == EarthStation.private_network_key:
                    print('[INFO] Storing message from {}'.format(content['reply_to']))
                    message_to_write = json.dumps({
                    'type': 'target',
                    'message': content_decrypted,
                    'to': 'Earth',
                    'from': content['reply_to']
                })
                    if not os.path.isdir(EarthStation.directory):
                        os.mkdir(EarthStation.directory)
                    with open(EarthStation.storage_location, 'a', encoding='utf-8') as f:
                        f.write(message_to_write)
                    if content_decrypted == 'New_Leader':
                        EarthStation.leader = content['reply_to']
            elif message and ('to' in message) and message['to'] == self.node_id and message['from'] == 'external':
                leader = EarthStation.leader
                #data_value = data.decode()
                #data_value = json.loads(data.decode())
                print('[INFO] Sending external network message to rovers ')
                print(message)
                #self._send_message_to_known_peer_no_error(self.host, leader_port, message)
                self.broadcast_request_earth(message['content'], leader, 'Earth')
                
            connection.close()
            soc.close()
            


    def start(self):
        print("needs to be changed")
        threading.Thread(target=self.storing_routing_data).start()
        
        
