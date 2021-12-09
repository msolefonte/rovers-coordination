import json
import random
import time
import uuid
from lib.components.SDNNode import SDNNode
from lib.utils.Encryptor import Encryptor
from lib.utils.constants import SLEEP_TIME_HEARTBEAT


class RoverRadio(SDNNode):
    def __init__(self, node_id, sdn_properties, physical_properties):
        super().__init__(node_id, sdn_properties, physical_properties)
        self.consumed_nonces = {}  # {nonce: timestamp}
        self.encryptor = Encryptor(physical_properties['encryption_key'])

    # Heartbeat

    def _start_heartbeat(self):
        while True:
            self.heartbeat(noerr=True)
            time.sleep(SLEEP_TIME_HEARTBEAT)

    def _handle_request(self, message, client_address):
        message['content'] = self.encryptor.decrypt(message['content'])
        self._handle_decrypted_request(message, client_address)

    def _handle_decrypted_request(self, message, client_address):
        raise NotImplementedError

    def broadcast(self, message, nonce=None, ttl=16, noerr=False):
        nonce = nonce if nonce else uuid.uuid4().hex
        message['nonce'] = nonce
        message['ttl'] = ttl

        # Artificial sleep to prevent all nodes broadcasting at the same time
        time.sleep(random.randint(0, 20) * 0.1)

        super()._broadcast(self.encryptor.encrypt(json.dumps(message)), noerr=noerr)
        self.consumed_nonces[nonce] = time.time()

    def broadcast_message_to(self, message, target_id, reply_to_id=None, nonce=None, ttl=16, noerr=False):
        if not self.networking_disabled:
            reply_to_id = reply_to_id if reply_to_id else self.node_id

            self.broadcast({
                'type': 'targeted-broadcast',
                'message': message,
                'to': target_id,
                'reply_to': reply_to_id if reply_to_id else self.node_id
            }, nonce, ttl, noerr)
        else:
            if not noerr:
                raise SystemError('Broadcasting disabled')

    def heartbeat(self, noerr=False):
        self.broadcast({'type': 'heartbeat', 'rover_id': self.node_id}, noerr=noerr)
