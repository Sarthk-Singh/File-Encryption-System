import streamlit as st  # used for web based front end
import requests  # for sending POST request to flask for comparison 
import os  # used for saving/reading files from system

from TextEncDec import (  # importing required functions for text encryption
    read_file,
    read_text_file,
    write_text_file,
    write_binary_file,
    encrypt_text_data,
    decrypt_text_data
)

from imageEncDec import (  # importing required functions for image encryption
    encrypt_image_data,
    decrypt_image_data
)

DOWNLOAD_DIR = "outputs"  # folder where output files will be saved
os.makedirs(DOWNLOAD_DIR, exist_ok=True)  # create folder if it doesn't exist

st.set_page_config(page_title="SecureCrypt", layout="wide")  # set page title and center the layout of the web page

st.title("🔐 SecureCrypt User Interface")  # display the main title of the page at the top

# create a sidebar with options for the type of operation user wants to perform
menu = st.sidebar.radio("Choose Operation", [
    "Encrypt Image",
    "Decrypt Image",
    "Encrypt Text File",
    "Decrypt Text File",
    "Compare Random vs Pseudo-Random"
])

def save_file(uploaded_file):  # function to save uploaded file into outputs folder
    path = os.path.join(DOWNLOAD_DIR, uploaded_file.name)  # generate full path using file name
    with open(path, "wb") as f:  # open file in write-binary mode
        f.write(uploaded_file.read())  # write file content to the destination path
    return path  # return path of saved file

# if user selects "Encrypt Image"
if menu == "Encrypt Image":
    st.header("🖼️ Encrypt Image")  # section title
    uploaded_file = st.file_uploader("Upload an image file", type=["png", "jpg", "jpeg", "bmp"])  # user uploads image
    use_pseudo = st.radio("Key Type", ["Random", "Pseudo-Random"])  # user selects key type

    if use_pseudo == "Pseudo-Random":  # if pseudo-random selected, ask for seed
        seed = st.text_input("Enter Seed Value: ")

    if uploaded_file and st.button("Encrypt"):  # when user uploads file and clicks encrypt
        img_path = save_file(uploaded_file)  # save file in outputs folder
        key_type = "pseudo" if use_pseudo == "Pseudo-Random" else "random"  # determine key type
        encrypted_data, key = encrypt_image_data(img_path, key_type=key_type, seed=seed if key_type == "pseudo" else None)  # encrypt the image

        enc_path = os.path.join(DOWNLOAD_DIR, uploaded_file.name + ".encimg")  # set path for encrypted image
        key_path = os.path.join(DOWNLOAD_DIR, uploaded_file.name + ".key.txt")  # set path for key file

        write_binary_file(enc_path, encrypted_data)  # save encrypted image to file
        write_text_file(key_path, key.hex())  # save key to file in hex format

        st.success("Image encrypted successfully!")  # show success message
        st.download_button("Download Encrypted Image", data=open(enc_path, "rb"), file_name=os.path.basename(enc_path))  # button to download encrypted file
        st.download_button("Download Key", data=open(key_path), file_name=os.path.basename(key_path))  # button to download key

# if user selects "Decrypt Image"
elif menu == "Decrypt Image":
    st.header("🖼️ Decrypt Image")  # section title
    enc_file = st.file_uploader("Upload Encrypted Image (.encimg)", type=["encimg"])  # user uploads encrypted image
    key_file = st.file_uploader("Upload Key (.txt)", type=["txt"])  # user uploads key file

    if enc_file and key_file and st.button("Decrypt"):  # when both files are uploaded and button clicked
        enc_path = save_file(enc_file)  # save encrypted file
        key_path = save_file(key_file)  # save key file
        key_hex = read_text_file(key_path)  # read key content
        decrypted = decrypt_image_data(enc_path, key_hex)  # decrypt the image
        out_path = enc_path.replace(".encimg", ".decrypted.jpg")  # create output file path

        write_binary_file(out_path, decrypted)  # save decrypted image to file
        st.success("Image decrypted successfully!")  # show success message
        st.image(out_path)  # preview the decrypted image
        st.download_button("Download Decrypted Image", data=open(out_path, "rb"), file_name=os.path.basename(out_path))  # download button

# if user selects "Encrypt Text File"
elif menu == "Encrypt Text File":
    st.header("📄 Encrypt Text File")  # section title
    uploaded_file = st.file_uploader("Upload a text file", type=["txt", "log", "csv"])  # user uploads text file
    use_pseudo = st.radio("Key Type", ["Random", "Pseudo-Random"])  # user selects key type

    if use_pseudo == "Pseudo-Random":
        seed = st.text_input("Enter Seed Value")  # ask for seed if pseudo is selected

    if uploaded_file and st.button("Encrypt"):  # when file is uploaded and encrypt clicked
        file_path = save_file(uploaded_file)  # save file to outputs
        data = read_file(file_path)  # read file content
        method = "pseudo" if use_pseudo == "Pseudo-Random" else "random"  # decide method based on user input
        encrypted, key = encrypt_text_data(data, method, seed if method == "pseudo" else None)  # encrypt the data
        encrypted_hex = encrypted.hex()  # convert encrypted bytes to hex string

        enc_file = file_path + ".enc.txt"  # path for encrypted file
        key_file = file_path + ".key.txt"  # path for key file

        write_text_file(enc_file, encrypted_hex)  # save encrypted content
        write_text_file(key_file, key.hex())  # save key

        st.success("Text encrypted successfully!")  # show message
        st.download_button("Download Encrypted Text", data=open(enc_file), file_name=os.path.basename(enc_file))  # download encrypted file
        st.download_button("Download Key", data=open(key_file), file_name=os.path.basename(key_file))  # download key file

# if user selects "Decrypt Text File"
elif menu == "Decrypt Text File":
    st.header("📄 Decrypt Text File")  # section title
    enc_file = st.file_uploader("Upload .enc.txt File", type=["txt"])  # upload encrypted text file
    key_file = st.file_uploader("Upload Key (.txt)", type=["txt"])  # upload key file

    if enc_file and key_file and st.button("Decrypt"):  # when both files uploaded and button clicked
        enc_path = save_file(enc_file)  # save encrypted file
        key_path = save_file(key_file)  # save key file
        enc_hex = read_text_file(enc_path)  # read encrypted file
        key_hex = read_text_file(key_path)  # read key file
        decrypted = decrypt_text_data(enc_hex, key_hex)  # decrypt the data
        out_path = enc_path.replace(".enc.txt", ".dec.txt")  # path for output decrypted file

        write_binary_file(out_path, decrypted)  # save decrypted file
        st.success("Decryption successful!")  # show message
        st.download_button("Download Decrypted File", data=open(out_path, "rb"), file_name=os.path.basename(out_path))  # download button

# if user selects "Compare Random vs Pseudo-Random"
elif menu == "Compare Random vs Pseudo-Random":
    st.header("📊 Compare Encryption Methods")  # section title
    uploaded_file = st.file_uploader("Upload any file to analyze", type=["txt", "csv", "jpg", "jpeg", "png", "bmp"])  # file to compare
    seed = st.text_input("Enter seed for pseudo-random key", value="pseudo123")  # default seed value

    if uploaded_file and st.button("Compare Now"):  # when file is uploaded and compare clicked
        file_path = save_file(uploaded_file)  # save file to local system
        with open(file_path, "rb") as f:
            files = {'file': (uploaded_file.name, f)}  # prepare file for sending
            data = {'seed': seed}  # attach seed with request
            response = requests.post("http://127.0.0.1:5000/compare", files=files, data=data)  # send request to flask backend

        if response.status_code == 200:  # if response is OK
            result = response.json()  # convert response to dictionary

            st.subheader("🔐 Random Key:")  # section title
            st.write(f"• Entropy: `{result['random']['entropy']}`")  # show entropy
            st.write(f"• Time: `{result['random']['encryption_time']}s`")  # show time

            st.subheader("🧬 Pseudo-Random Key:")  # section title
            st.write(f"• Entropy: `{result['pseudo_random']['entropy']}`")  # show entropy
            st.write(f"• Time: `{result['pseudo_random']['encryption_time']}s`")  # show time

            st.success(result["recommended"])  # show final recommendation
        else:
            st.error("Server error: " + response.text)  # show error message if request fails
