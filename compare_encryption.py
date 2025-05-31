import os
import time
import math
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd
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
    # If data is hex string, convert to bytes
    if isinstance(data, str):
        data = bytes.fromhex(data)
    counter = Counter(data)
    length = len(data)
    # Shannon entropy formula
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

# Generate a comparison bar chart for entropy, encryption time, and file size
def generate_comparison_chart(rand, pseudo):
    labels = ['Entropy', 'Encryption Time (s)', 'File Size (bytes)']
    random_values = [rand['entropy'], rand['encryption_time'], rand['file_size']]
    pseudo_values = [pseudo['entropy'], pseudo['encryption_time'], pseudo['file_size']]

    x = range(len(labels))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar([i - width/2 for i in x], random_values, width, label='Random Key')
    ax.bar([i + width/2 for i in x], pseudo_values, width, label='Pseudo-Random Key')

    ax.set_ylabel('Values')
    ax.set_title('Encryption Comparison Metrics')
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.legend()
    chart_path = os.path.join(UPLOAD_FOLDER, 'comparison_chart.png')
    plt.savefig(chart_path)
    plt.close()
    return chart_path

# Generate an HTML table summarizing the comparison
def generate_comparison_table(rand, pseudo):
    data = {
        "Metric": ["Entropy", "Encryption Time (s)", "Encrypted File Size (bytes)", "Decrypted File Path"],
        "Random Key": [rand['entropy'], rand['encryption_time'], rand['file_size'], rand['decrypted_file']],
        "Pseudo-Random Key": [pseudo['entropy'], pseudo['encryption_time'], pseudo['file_size'], pseudo['decrypted_file']]
    }
    df = pd.DataFrame(data)
    return df.to_html(index=False)

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

    # Determine which has higher entropy for recommendation
    winner = "random" if rand_results["entropy"] > pseudo_results["entropy"] else "pseudo_random"

    # Generate comparison chart and table
    chart_path = generate_comparison_chart(rand_results, pseudo_results)
    html_table = generate_comparison_table(rand_results, pseudo_results)

    # Return JSON with results, chart URL, and table HTML
    return jsonify({
        "status": "success",
        "random": rand_results,
        "pseudo_random": pseudo_results,
        "recommended": f"{winner} key encryption shows higher entropy and may be more secure.",
        "comparison_chart": "/get_chart",  # endpoint to retrieve the saved chart image
        "comparison_table": html_table
    })

# Route to serve the generated comparison chart image
@app.route('/get_chart')
def get_chart():
    chart_path = os.path.join(UPLOAD_FOLDER, 'comparison_chart.png')
    if os.path.exists(chart_path):
        return send_file(chart_path, mimetype='image/png')
    return "Chart not found", 404

# Entry point for running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
