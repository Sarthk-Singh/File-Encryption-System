
import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
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

# Encrypt and decrypt a file using a truly random key
def random_encrypt(file_path, is_text):
    data = read_file(file_path)
    key = generate_random_key(len(data))
    encrypted = xor_encrypt_decrypt(data, key)

    # Generate appropriate filenames
    enc_ext = ".rand.enc.txt" if is_text else ".rand.encimg"
    dec_ext = ".rand.dec.txt" if is_text else ".rand.decrypted.jpg"
    enc_file = file_path + enc_ext
    key_file = file_path + ".rand.key.txt"
    dec_file = file_path + dec_ext

    # Save encrypted and decrypted output based on file type
    if is_text:
        write_text_file(enc_file, encrypted.hex())  # Save encrypted data as hex
    else:
        write_binary_file(enc_file, encrypted)  # Save raw binary for images

    write_text_file(key_file, key.hex())  # Save key in hex format
    decrypted = xor_encrypt_decrypt(encrypted, key)
    write_binary_file(dec_file, decrypted)  # Save decrypted file

    return enc_file, key_file, dec_file

# Encrypt and decrypt a file using a pseudo-random key (deterministic from seed)
def pseudo_encrypt(file_path, is_text, seed):
    data = read_file(file_path)
    key = generate_pseudo_random_key(seed, len(data))
    encrypted = xor_encrypt_decrypt(data, key)

    enc_ext = ".pseudo.enc.txt" if is_text else ".pseudo.encimg"
    dec_ext = ".pseudo.dec.txt" if is_text else ".pseudo.decrypted.jpg"
    enc_file = file_path + enc_ext
    key_file = file_path + ".pseudo.key.txt"
    dec_file = file_path + dec_ext

    if is_text:
        write_text_file(enc_file, encrypted.hex())
    else:
        write_binary_file(enc_file, encrypted)

    write_text_file(key_file, key.hex())
    decrypted = xor_encrypt_decrypt(encrypted, key)
    write_binary_file(dec_file, decrypted)

    return enc_file, key_file, dec_file

# Route to receive file and perform encryption/decryption comparison
@app.route('/compare', methods=['POST'])
def compare_file():
    # Check if file is provided in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    uploaded_file = request.files['file']
    seed = request.form.get('seed', 'default_seed')  # Use default if seed not given

    if uploaded_file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # Secure the filename and save it to server
    filename = secure_filename(uploaded_file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(file_path)

    # Determine if the uploaded file is text or binary
    is_text = is_text_file(file_path)

    # --- RANDOM ENCRYPTION PROCESS ---
    rand_enc, rand_key, rand_dec = random_encrypt(file_path, is_text)

    # --- PSEUDO-RANDOM ENCRYPTION PROCESS ---
    pseudo_enc, pseudo_key, pseudo_dec = pseudo_encrypt(file_path, is_text, seed)

    # Return file paths for all results in a JSON response
    return jsonify({
        "status": "success",
        "random": {
            "encrypted": rand_enc,
            "key": rand_key,
            "decrypted": rand_dec
        },
        "pseudo_random": {
            "encrypted": pseudo_enc,
            "key": pseudo_key,
            "decrypted": pseudo_dec
        }
    })

# Entry point for running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
