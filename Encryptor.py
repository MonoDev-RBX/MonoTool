from cryptography.fernet import Fernet
import base64, hashlib

def derive_key(password):
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

class Encryptor:
    @staticmethod
    def encrypt(data, password):
        return Fernet(derive_key(password)).encrypt(data)

    @staticmethod
    def decrypt(data, password):
        return Fernet(derive_key(password)).decrypt(data)
