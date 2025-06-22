import os
import secrets
import random

def xor_encrypt_decrypt(data, key):
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def generate_random_key(length):
    return secrets.token_bytes(length)

def generate_pseudo_random_key(seed, length):
    random.seed(seed)
    return bytes([random.randint(0, 255) for _ in range(length)])

def read_file(filename):
    with open(filename, 'rb') as file:
        return file.read()

def write_text_file(filename, text):
    with open(filename, 'w') as file:
        file.write(text)

def read_text_file(filename):
    with open(filename, 'r') as file:
        return file.read()

def write_binary_file(filename, data):
    with open(filename, 'wb') as file:
        file.write(data)

def encrypt_text_data(data, method, seed=None):
    if method == "random":
        key = generate_random_key(len(data))
    elif method == "pseudo" and seed:
        key = generate_pseudo_random_key(seed, len(data))
    else:
        raise ValueError("Invalid method or missing seed")

    encrypted = xor_encrypt_decrypt(data, key)
    return encrypted, key

def decrypt_text_data(encrypted_hex, key_hex):
    encrypted = bytes.fromhex(encrypted_hex)
    key = bytes.fromhex(key_hex)
    decrypted = xor_encrypt_decrypt(encrypted, key)
    return decrypted