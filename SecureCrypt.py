import streamlit as st  # used for web based front end
import requests  # for sending POST request to flask for comparison 
import os  # used for saving/reading files from system

from TextEncDec import (  # importing the functions 
    xor_encrypt_decrypt,
    generate_random_key,
    generate_pseudo_random_key,
    read_file,
    read_text_file,
    write_text_file,
    write_binary_file
)

# create a folder "outputs" to store the encrypted/decrypted files
DOWNLOAD_DIR = "outputs"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="SecureCrypt", layout="centered")  # set page title and center the layout of the web page

st.title("🔐 SecureCrypt User Interface")  # Display the main title of the page at the top of the pages

# creates a sidebar with radio buttons that allows user to choose the operation they wants to perform on the files
# the ui will change based on the users selection
menu = st.sidebar.radio("Choose Operation", [
    "Encrypt Image",
    "Decrypt Image",
    "Encrypt Text File",
    "Decrypt Text File",
    "Compare Random vs Pseudo-Random"
    ])

def save_file(uploaded_file):  # function for saving files to our system
    path = os.path.join(DOWNLOAD_DIR, uploaded_file.name)  # create a path to the folder where the files are to be saved
    with open(path, "wb") as f:  # open file in write-binary mode (to handle images)
        f.write(uploaded_file.read())  # write content of generated file in the opened file
    return path  # return the saved file path to be used later

# if Encrypt Image menu is selected from side bar
if menu == "Encrypt Image":
    st.header("🖼️ Encrypt Image")  # title of the page
    uploaded_file = st.file_uploader("Upload an image file", type=["png", "jpg", "jpeg", "bmp"])  # let user upload image file in these formats
    use_pseudo = st.radio("Key Type", ["Random", "Pseudo-Random"])  # using radio buttons, ask user for type of key to use for encryption

    if use_pseudo == "Pseudo-Random":  # if pseudo random key is selected, ask user for seed value
        seed = st.text_input("Enter Seed Value: ")

    if uploaded_file and st.button("Encrypt"):  # when file is entered and user click encrypt button
        img_path = save_file(uploaded_file)  # call save_file() function and save file to the outputs folder
        key = generate_pseudo_random_key(seed, os.path.getsize(img_path)) if use_pseudo == "Pseudo-Random" else generate_random_key(os.path.getsize(img_path))  # generate key accordingly
        data = read_file(img_path)  # reads image data
        encrypted_data = xor_encrypt_decrypt(data, key)  # perform XOR encryption
        # build files for encrypted image and its key for decryption
        enc_path = os.path.join(DOWNLOAD_DIR, uploaded_file.name + ".encimg")
        key_path = os.path.join(DOWNLOAD_DIR, uploaded_file.name + ".key.txt")
        # save these files to the system
        write_binary_file(enc_path, encrypted_data)
        write_text_file(key_path, key.hex())
        # gives a successful message and give user two button to download these two files
        st.success("Image encrypted successfully!")
        st.download_button("Download Encrypted Image", data=open(enc_path, "rb"), file_name=os.path.basename(enc_path))
        st.download_button("Download Key", data=open(key_path), file_name=os.path.basename(key_path))

# Decrypt Image 
elif menu == "Decrypt Image":
    st.header("🖼️ Decrypt Image")  # title of the page
    enc_file = st.file_uploader("Upload Encrypted Image (.encimg)", type=["encimg"])  # upload encrypted image
    key_file = st.file_uploader("Upload Key (.txt)", type=["txt"])  # upload key used during encryption

    if enc_file and key_file and st.button("Decrypt"):  # proceed when both files are selected
        enc_path = save_file(enc_file)  # save encrypted image
        key_path = save_file(key_file)  # save key file
        data = read_file(enc_path)  # read image data
        key = bytes.fromhex(read_text_file(key_path))  # convert key from hex to bytes

        if len(key) != len(data):  # verify key size
            st.error("Key and data length mismatch!")  # show error if sizes don't match
        else:
            decrypted = xor_encrypt_decrypt(data, key)  # perform decryption
            out_path = enc_path.replace(".encimg", ".decrypted.jpg")  # output filename
            write_binary_file(out_path, decrypted)  # save decrypted image
            st.success("Image decrypted successfully!")
            st.image(out_path)  # preview image on screen
            st.download_button("Download Decrypted Image", data=open(out_path, "rb"), file_name=os.path.basename(out_path))  # download button

# Encrypt Text 
elif menu == "Encrypt Text File":
    st.header("📄 Encrypt Text File")  # title of the page
    uploaded_file = st.file_uploader("Upload a text file", type=["txt", "log", "csv"])  # upload any valid text file
    use_pseudo = st.radio("Key Type", ["Random", "Pseudo-Random"])  # ask user to choose key type

    if use_pseudo == "Pseudo-Random":
        seed = st.text_input("Enter Seed Value")  # input seed value for deterministic key

    if uploaded_file and st.button("Encrypt"):
        file_path = save_file(uploaded_file)  # save uploaded file
        data = read_file(file_path)  # read file content
        key = generate_pseudo_random_key(seed, len(data)) if use_pseudo == "Pseudo-Random" else generate_random_key(len(data))  # generate key
        encrypted = xor_encrypt_decrypt(data, key)  # encrypt using XOR
        encrypted_hex = encrypted.hex()  # convert to hex for readable storage

        enc_file = file_path + ".enc.txt"  # encrypted file name
        key_file = file_path + ".key.txt"  # key file name
        write_text_file(enc_file, encrypted_hex)  # save encrypted data
        write_text_file(key_file, key.hex())  # save key

        st.success("Text encrypted successfully!")  # show success
        st.download_button("Download Encrypted Text", data=open(enc_file), file_name=os.path.basename(enc_file))  # download button for data
        st.download_button("Download Key", data=open(key_file), file_name=os.path.basename(key_file))  # download button for key

# Decrypt Text 
elif menu == "Decrypt Text File":
    st.header("📄 Decrypt Text File")  # title
    enc_file = st.file_uploader("Upload .enc.txt File", type=["txt"])  # encrypted file
    key_file = st.file_uploader("Upload Key (.txt)", type=["txt"])  # key file

    if enc_file and key_file and st.button("Decrypt"):  # proceed when both are given
        enc_path = save_file(enc_file)  # save encrypted file
        key_path = save_file(key_file)  # save key file
        try:
            encrypted = bytes.fromhex(read_text_file(enc_path))  # convert hex to bytes
            key = bytes.fromhex(read_text_file(key_path))  # convert key
            decrypted = xor_encrypt_decrypt(encrypted, key)  # decrypt
            out_path = enc_path.replace(".enc.txt", ".dec.txt")  # output filename
            write_binary_file(out_path, decrypted)  # save result
            st.success("Decryption successful!")
            st.download_button("Download Decrypted File", data=open(out_path, "rb"), file_name=os.path.basename(out_path))  # download option
        except Exception as e:
            st.error(f"Error: {e}")  # show error message if any issue occurs

# -------- Compare Encryption --------
elif menu == "Compare Random vs Pseudo-Random":
    st.header("📊 Compare Encryption Methods")  # title of the comparison page
    uploaded_file = st.file_uploader("Upload any file to analyze", type=["txt", "csv", "jpg", "jpeg", "png", "bmp"])  # upload file for analysis
    seed = st.text_input("Enter seed for pseudo-random key", value="pseudo123")  # input seed value

    if uploaded_file and st.button("Compare Now"):  # proceed when both are provided
        file_path = save_file(uploaded_file)  # save the file to local outputs/
        with open(file_path, "rb") as f:
            files = {'file': (uploaded_file.name, f)}  # prepare file data for sending
            data = {'seed': seed}  # seed to be sent to server
            response = requests.post("http://127.0.0.1:5000/compare", files=files, data=data)  # send post request to Flask backend

        if response.status_code == 200:  # if success (code 200)
            result = response.json()  # read returned JSON

            # Show stats for random key
            st.subheader("🔐 Random Key:")
            st.write(f"• Entropy: `{result['random']['entropy']}`")
            st.write(f"• Time: `{result['random']['encryption_time']}s`")

            # Show stats for pseudo-random key
            st.subheader("🧬 Pseudo-Random Key:")
            st.write(f"• Entropy: `{result['pseudo_random']['entropy']}`")
            st.write(f"• Time: `{result['pseudo_random']['encryption_time']}s`")

            # Suggest which key type seems more secure
            st.success(result["recommended"])
        else:
            st.error("Server error: " + response.text)  # handle request failure
