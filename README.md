# 🔐 SecureCrypt – Streamlit-Based Encryption System

Welcome to **SecureCrypt** – an interactive, browser-based encryption and decryption platform built with **Streamlit**.  
This system allows users to securely perform **random and pseudo-random key-based XOR encryption** on both image and text files, and compare their security characteristics.

---

## 🚀 Project Overview

**SecureCrypt** provides a hands-on playground for understanding how cryptographic key generation affects data security.  
With support for both **truly random** and **deterministically generated (pseudo-random)** keys, this system lets users:

- 🔐 Encrypt/Decrypt files with full control  
- 📊 Analyze key entropy and encryption time  
- 📈 Compare security outcomes visually and statistically

---

## 🧠 Features

- 🖼 **Encrypt/Decrypt Images** with XOR logic using random or pseudo-random keys  
- 📄 **Encrypt/Decrypt Text Files** (`.txt`, `.csv`, `.log` supported)  
- 🎲 **Random Key Generation** using Python's `secrets` module  
- 🤖 **Pseudo-Random Key Generation** using `random` with a user-defined seed  
- 📊 **Compare Key Entropy & Performance** (via integrated Flask API)  
- 💾 **File download and preview** support  
- 💡 **Simple, elegant GUI** built using Streamlit  

---

## ⚙ How It Works

1. **Select Operation**: Choose from image/text encryption, decryption, or key comparison  
2. **Upload Files**: Provide your source files and key/seed where required  
3. **Choose Key Type**: Select random or pseudo-random key for the operation  
4. **Download Results**: Get encrypted/decrypted files and the generated keys  
5. **Compare Security**: Evaluate entropy and encryption speed for both key types  

---

## 🖥 Interface Preview

The interface offers:

- ✅ Sidebar navigation for operation selection  
- ✅ File uploader widgets for source and key files  
- ✅ Download buttons for encrypted/decrypted outputs  
- ✅ Entropy and encryption time display in comparison view  

---

## 🛠 Setup & Running the Project

### 🔃 Backend (Flask API for entropy comparison)

Start the comparison server:
```bash
python compare_encryption.py
```

### 🌐 Frontend (Streamlit GUI)

In a new terminal, run the frontend:
```
streamlit run SecureCrypt.py
```
This will launch the user interface in your default browser at http://localhost:8501.

---

### 📂 Project Structure

```
SecureCrypt/
├── compare_encryption.py
├── imageEncDec.py
├── imageEncDec.py
├── SecureCrypt.py
└── README.md
```

---

### 🔐 Notes

- Keep your keys secure; random keys offer stronger security but are harder to reproduce
- Pseudo-random keys enable repeatable encryption with the same seed
- Use the comparison feature to understand key entropy and encryption speed tradeoffs

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

---

## 📬 Contact

For questions or collaborations, reach out via [GitHub](https://github.com/Sarthk-Singh).
