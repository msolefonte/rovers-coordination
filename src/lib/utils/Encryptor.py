from cryptography.fernet import Fernet


class Encryptor:
    def __init__(self, encryption_key):
        self.fernet = Fernet(encryption_key.encode())

    def encrypt(self, message):
        return self.fernet.encrypt(message.encode()).decode()

    def decrypt(self, encrypted_message):
        return self.fernet.decrypt(encrypted_message.encode()).decode()
