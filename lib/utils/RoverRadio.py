import json
import random
import time
import uuid
from .Encryptor import Encryptor
from .SDNNode import SDNNode


class RoverRadio(SDNNode):
    def __init__(self, node_id, location, host, port, known_peers, radio_range, encryption_key):
        super().__init__(node_id, location, host, port, known_peers, radio_range)
        self.consumed_nonces = {}  # {nonce: timestamp}
        self.encryptor = Encryptor(encryption_key)

    def broadcast(self, message, nonce=None, ttl=16):
        nonce = nonce if nonce else uuid.uuid4().hex
        message['nonce'] = nonce
        message['ttl'] = ttl

        # Artificial sleep to prevent all nodes broadcasting at the same time
        time.sleep(random.randint(0, 20) * 0.1)

        super().broadcast(self.encryptor.encrypt(json.dumps(message)))
        self.consumed_nonces[nonce] = time.time()

    def broadcast_message_to(self, message, target_id, reply_to_id=None, nonce=None, ttl=16):
        if not self.networking_disabled:
            reply_to_id = reply_to_id if reply_to_id else self.node_id

            # print('[DEBU] Broadcasting message targeting', target_id + '. (Origin', reply_to_id + ')')

            self.broadcast({
                'type': 'targeted-broadcast',
                'message': message,
                'to': target_id,
                'reply_to': reply_to_id if reply_to_id else self.node_id
            }, nonce, ttl)
        else:
            raise SystemError('Broadcasting disabled')

    def heartbeat(self):
        self.broadcast({'type': 'heartbeat', 'rover_id': self.node_id})

    def _handle_request(self, message, client_address):
        message['content'] = self.encryptor.decrypt(message['content'])
        self._handle_decrypted_request(message, client_address)

    def _handle_decrypted_request(self, message, client_address):
        raise NotImplementedError
