import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

class SecureMessenger:
    #Handles AES-GCM encryption/decryption once a key is established.
    def __init__(self, key: bytes):
        self.aesgcm = AESGCM(key)

    def encrypt(self, message: str) -> bytes:
        nonce = os.urandom(12)
        ciphertext = self.aesgcm.encrypt(nonce, message.encode(), None)
        return nonce + ciphertext

    def decrypt(self, encrypted_data: bytes) -> str:
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        return self.aesgcm.decrypt(nonce, ciphertext, None).decode()

def decrypt_key_with_rsa(private_key, encrypted_aes_key):
    #Server-side helper to unlock the AES key sent by client.
    return private_key.decrypt(
        encrypted_aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )