import random
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

# --- Image Encryption ---

def encrypt_image(img_path, use_pseudo=False, seed=None):
    if not os.path.exists(img_path):
        raise FileNotFoundError("Image file not found.")

    data = read_file(img_path)

    if use_pseudo:
        if not seed:
            raise ValueError("Seed value is required for pseudo-random key.")
        key = generate_pseudo_random_key(seed, len(data))
    else:
        key = generate_random_key(len(data))

    encrypted_data = xor_encrypt_decrypt(data, key)

    enc_file = img_path + ".encimg"
    key_file = img_path + ".key.txt"

    write_binary_file(enc_file, encrypted_data)
    write_text_file(key_file, key.hex())

    print(f"Image encrypted and saved as: {enc_file}")
    print(f"Key saved to: {key_file}")

# --- Image Decryption ---

def decrypt_image(enc_path, key_path):
    if not os.path.exists(enc_path) or not os.path.exists(key_path):
        raise FileNotFoundError("Encrypted file or key file not found.")

    encrypted_data = read_file(enc_path)
    key_hex = read_text_file(key_path)
    key = bytes.fromhex(key_hex)

    if len(key) != len(encrypted_data):
        raise ValueError("Key length and encrypted data length mismatch.")

    decrypted_data = xor_encrypt_decrypt(encrypted_data, key)

    # Save as decrypted original image
    if enc_path.endswith(".encimg"):
        output_file = enc_path.replace(".encimg", ".decrypted.jpg")
    else:
        output_file = enc_path + ".decrypted.jpg"

    write_binary_file(output_file, decrypted_data)
    print(f"Image decrypted and saved as: {output_file}")

# --- Example (uncomment to use directly) ---
#encrypt_image("/Users/sarthaksingh/Documents/Project/File Encryption System/sample.jpg", use_pseudo=True, seed="mypassword123")
decrypt_image("/Users/sarthaksingh/Documents/Project/File Encryption System/sample.jpg.encimg", "/Users/sarthaksingh/Documents/Project/File Encryption System/sample.jpg.key.txt")