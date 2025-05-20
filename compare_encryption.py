import os
import time
import math
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from collections import Counter
from TextEncDec import (
    xor_encrypt_decrypt,
    generate_random_key,
    generate_pseudo_random_key,
    read_file,
    write_text_file,
    write_binary_file
)

# Initialize Flask app
app = Flask(__name__)

# Folder where uploaded files will be stored
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper function to detect if a file is a text file based on its extension
def is_text_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    return ext in ['.txt', '.csv', '.log', '.json']

# Function to calculate Shannon entropy of data
def calculate_entropy(data):
    if isinstance(data, str):
        data = bytes.fromhex(data)
    counter = Counter(data)
    length = len(data)
    entropy = -sum(count/length * math.log2(count/length) for count in counter.values())
    return round(entropy, 4)

# Encrypt and decrypt a file using a truly random key
def random_encrypt(file_path, is_text):
    data = read_file(file_path)
    key = generate_random_key(len(data))

    start_time = time.perf_counter()
    encrypted = xor_encrypt_decrypt(data, key)
    encryption_time = round(time.perf_counter() - start_time, 6)

    enc_ext = ".rand.enc.txt" if is_text else ".rand.encimg"
    dec_ext = ".rand.dec.txt" if is_text else ".rand.decrypted.jpg"
    enc_file = file_path + enc_ext
    key_file = file_path + ".rand.key.txt"
    dec_file = file_path + dec_ext

    if is_text:
        encrypted_hex = encrypted.hex()
        write_text_file(enc_file, encrypted_hex)
        entropy = calculate_entropy(encrypted_hex)
    else:
        write_binary_file(enc_file, encrypted)
        entropy = calculate_entropy(encrypted)

    write_text_file(key_file, key.hex())
    decrypted = xor_encrypt_decrypt(encrypted, key)
    write_binary_file(dec_file, decrypted)

    return {
        "encrypted_file": enc_file,
        "key_file": key_file,
        "decrypted_file": dec_file,
        "encryption_time": encryption_time,
        "entropy": entropy,
        "file_size": os.path.getsize(enc_file)
    }

# Encrypt and decrypt a file using a pseudo-random key (deterministic from seed)
def pseudo_encrypt(file_path, is_text, seed):
    data = read_file(file_path)
    key = generate_pseudo_random_key(seed, len(data))

    start_time = time.perf_counter()
    encrypted = xor_encrypt_decrypt(data, key)
    encryption_time = round(time.perf_counter() - start_time, 6)

    enc_ext = ".pseudo.enc.txt" if is_text else ".pseudo.encimg"
    dec_ext = ".pseudo.dec.txt" if is_text else ".pseudo.decrypted.jpg"
    enc_file = file_path + enc_ext
    key_file = file_path + ".pseudo.key.txt"
    dec_file = file_path + dec_ext

    if is_text:
        encrypted_hex = encrypted.hex()
        write_text_file(enc_file, encrypted_hex)
        entropy = calculate_entropy(encrypted_hex)
    else:
        write_binary_file(enc_file, encrypted)
        entropy = calculate_entropy(encrypted)

    write_text_file(key_file, key.hex())
    decrypted = xor_encrypt_decrypt(encrypted, key)
    write_binary_file(dec_file, decrypted)

    return {
        "encrypted_file": enc_file,
        "key_file": key_file,
        "decrypted_file": dec_file,
        "encryption_time": encryption_time,
        "entropy": entropy,
        "file_size": os.path.getsize(enc_file)
    }

# Route to receive file and perform encryption/decryption comparison
@app.route('/compare', methods=['POST'])
def compare_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    uploaded_file = request.files['file']
    seed = request.form.get('seed', 'default_seed')

    if uploaded_file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(uploaded_file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(file_path)

    is_text = is_text_file(file_path)

    # RANDOM ENCRYPTION PROCESS
    rand_results = random_encrypt(file_path, is_text)

    # PSEUDO-RANDOM ENCRYPTION PROCESS
    pseudo_results = pseudo_encrypt(file_path, is_text, seed)

    # Determine which has higher entropy
    winner = "random" if rand_results["entropy"] > pseudo_results["entropy"] else "pseudo_random"

    return jsonify({
        "status": "success",
        "random": rand_results,
        "pseudo_random": pseudo_results,
        "recommended": f"{winner} key encryption shows higher entropy and may be more secure."
    })

# Entry point for running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
