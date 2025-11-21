# WiComm/encryption/aes_utils.py

from Cryptodome.Cipher import AES
from Crypto.Random import get_random_bytes


def generate_key():
    return get_random_bytes(32)


def encrypt_data(data, key):
    try:
        cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return cipher.nonce + tag + ciphertext
    except ValueError as e:
        print(f"Encryption error: {e}. Key length must be 16, 24, or 32 bytes.")
        return None


def decrypt_data(encrypted_data, key):
    try:
        nonce_len = 16
        tag_len = 16

        nonce = encrypted_data[:nonce_len]
        tag = encrypted_data[nonce_len:nonce_len + tag_len]
        ciphertext = encrypted_data[nonce_len + tag_len:]

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext
    except ValueError as e:
        print(f"Decryption error: {e}. Data may have been tampered with or key is incorrect.")
        return None