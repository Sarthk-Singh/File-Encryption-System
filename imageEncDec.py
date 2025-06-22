import os
from TextEncDec import (
    xor_encrypt_decrypt,
    generate_random_key,
    generate_pseudo_random_key,
    read_file,
    read_text_file,
    write_text_file,
    write_binary_file
)

def encrypt_image_data(img_path, key_type="random", seed=None):
    if not os.path.exists(img_path):
        raise FileNotFoundError("Image file does not exist.")

    if key_type == "pseudo":
        if not seed:
            raise ValueError("Seed is required for pseudo-random key.")
        key = generate_pseudo_random_key(seed, os.path.getsize(img_path))
    else:
        key = generate_random_key(os.path.getsize(img_path))

    data = read_file(img_path)
    encrypted_data = xor_encrypt_decrypt(data, key)
    return encrypted_data, key

def decrypt_image_data(enc_path, key_hex):
    if not os.path.exists(enc_path):
        raise FileNotFoundError("Encrypted image file does not exist.")

    encrypted_data = read_file(enc_path)
    key = bytes.fromhex(key_hex)

    if len(key) != len(encrypted_data):
        raise ValueError("Key length and data length mismatch.")

    decrypted_data = xor_encrypt_decrypt(encrypted_data, key)
    return decrypted_data