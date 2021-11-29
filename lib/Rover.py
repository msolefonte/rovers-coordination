import json
import random
import threading
import time
from utils.SDNNode import SDNNode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class Rover(SDNNode):
    """
    rover_id - id, host - host, port - port
    known_peers = host:port,host:port // For simulation purposes
    operation_area - 0,0,999,999 // Coordinates that defines the operation area. Second point always bigger
    speed - 20
    """

    
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
            ct=Rover.private_network_key+ct.hex()
        else:
            ct=Rover.public_network_key+ct.hex()
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
            if (ct_key == Rover.private_network_key) or (ct_key == Rover.public_network_key):
                ct_value = bytes.fromhex(st[9:])
                msg = decryptor.update(ct_value) + decryptor.finalize()
                msg_decoded = str(msg,'utf-8').rstrip()
            else:
                msg_decoded =st
                #print('[WARN] [SDN] Unautorized message, ignoring the message:'+st)
        except Exception as e:
            print('[WARN] [SDN] Invalid encryptions (possible injections), ignoring the message', e, flush=True)    
        return ct_key , msg_decoded

    def __init__(self, rover_id, host, port, known_peers, operation_area, max_speed, radio_range):
        self.operation_area = [
            [int(operation_area.split(',')[0]), int(operation_area.split(',')[1])],
            [int(operation_area.split(',')[2]), int(operation_area.split(',')[3])]
        ]
        super().__init__(rover_id, {
            'x': random.randint(self.operation_area[0][0], self.operation_area[1][0]),
            'y': random.randint(self.operation_area[0][1], self.operation_area[1][1])
        }, host, int(port), known_peers.split(',') if known_peers != '' else [], radio_range)

        # Sensors
        self.max_speed = max_speed
        self.speedometer = {'x': 0, 'y': 0}

        # Status
        self.movement_enabled = True
        self.low_battery_mode = False


    def _move(self):
        x_movement = random.randint(0, self.max_speed) * (1 if random.random() < 0.5 else -1)
        y_movement = random.randint(0, self.max_speed) * (1 if random.random() < 0.5 else -1)

        if self.location['x'] + x_movement < self.operation_area[0][0]:
            x_movement = self.operation_area[0][0] - self.location['x']
        if self.location['x'] + x_movement > self.operation_area[1][0]:
            x_movement = self.operation_area[1][0] - self.location['x']
        if self.location['y'] + y_movement < self.operation_area[0][1]:
            y_movement = self.operation_area[0][1] - self.location['y']
        if self.location['y'] + y_movement > self.operation_area[1][1]:
            y_movement = self.operation_area[1][1] - self.location['y']

        self.location = {'x': self.location['x'] + x_movement, 'y': self.location['y'] + y_movement}
        self.speedometer = {'x': x_movement, 'y': y_movement}

    def _start_engine(self):
        turns_spent_recharging = 0
        while True:
            # The battery has a 5% probability of getting empty. Once empty, the rover enters in the low battery mode
            # and spends three turns in the same location.
            if self.low_battery_mode:
                if turns_spent_recharging >= 3:
                    self.low_battery_mode = False
                    self.networking_disabled = False
                    print('[INFO] Battery recharged. Low battery mode disabled', flush=True)
            elif random.randint(0, 100) < 5:
                print('[INFO] Battery low. Deploying solar panels', flush=True)
                self.low_battery_mode = True
                self.networking_disabled = True

            if not self.low_battery_mode:
                turns_spent_recharging = 0
                if self.movement_enabled:
                    self._move()
                    print('[INFO] Rover moved to new location', flush=True)
                    # print('[DEBU] Positioning System lecture:', self.location, flush=True)
                    # print('[DEBU] Speedometer lecture:', self.speedometer, flush=True)
            else:
                print('[INFO] Recharging...', flush=True)
                turns_spent_recharging += 1
            time.sleep(30)

    def broadcast_request(self,message,target):
        message_encrypted = Rover.encrypt_message(message,Rover.private_key,Rover.private_iv)
        self.broadcast_message_to(message_encrypted,target)

    def _handle_request(self, message, client_address):
        # print('[DEBU] Received message from', client_address[0] + ':' + str(client_address[1]) +
        #      ':', message, flush=True)
        
        content = json.loads(message['content'])       
        if content['type'] == 'heartbeat':
            pass  # Good to know I guess. Maybe useful for something
        elif content['type'] == 'target' and content['nonce'] not in self.consumed_nonces.keys():
            self.consumed_nonces[content['nonce']] = time.time()
            if content['to'] == self.node_id:
                
                content_key,content_decrypted = Rover.decrypt_message(self,content['message'],Rover.private_key,Rover.private_iv)
                print('[INFO] That content({}) was for me({}), so nice! Thank you {}'.format(content_decrypted,self.node_id,content['reply_to']))
            else:
                ttl = content['ttl'] - 1
                if ttl >= 0:
                    self.broadcast_message_to(content['message'], content['to'], content['reply_to'], content['nonce'], ttl)

    def start(self):
        threading.Thread(target=self._start_server).start()
        if self.node_id != 'network-visualizer':
            threading.Thread(target=self._start_engine).start()

    