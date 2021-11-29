import json
import time
import uuid
from .Encryptor import Encryptor
from .SDNNode import SDNNode


class RoverRadio(SDNNode):
    def __init__(self, node_id, location, host, port, known_peers, radio_range, encryption_key):
        super().__init__(node_id, location, host, port, known_peers, radio_range)
        self.consumed_nonces = {}  # {nonce: timestamp}
        self.encryptor = Encryptor(encryption_key)

    def broadcast(self, message):
        super().broadcast(self.encryptor.encrypt(message))

    def broadcast_message_to(self, message, target_id, reply_to_id=None, nonce=None, ttl=16):
        if not self.networking_disabled:
            nonce = nonce if nonce else uuid.uuid4().hex
            reply_to_id = reply_to_id if reply_to_id else self.node_id

            print('[INFO] Broadcasting message targeting', target_id + '. (Origin', reply_to_id + ')')

            self.broadcast(json.dumps({
                'type': 'target',
                'message': message,
                'to': target_id,
                'reply_to': reply_to_id if reply_to_id else self.node_id,
                'nonce': nonce,
                'ttl': ttl
            }))

            self.consumed_nonces[nonce] = time.time()
        else:
            raise SystemError('Broadcasting disabled')

    def heartbeat(self):
        self.broadcast(json.dumps({'type': 'heartbeat'}))

    def _handle_request(self, message, client_address):
        message['content'] = self.encryptor.decrypt(message['content'])
        self._handle_decrypted_request(message, client_address)

    def _handle_decrypted_request(self, message, client_address):
        raise NotImplementedError
