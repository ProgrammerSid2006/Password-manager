# 🔐 Password Manager (CLI-Based)

A secure CLI-based Password Manager built with **Python and MongoDB**, implementing
**industry-standard security architecture**.

The application uses **SHA-256 hashing** for master password authentication and
**AES (Fernet) encryption** for secure password storage and retrieval.

---

## 🚀 Features
- Master password authentication
- AES-encrypted password storage
- Secure password retrieval
- MongoDB NoSQL backend
- Full CRUD operations
- Indexed queries for fast access

---

## 🛠 Tech Stack
- Python
- MongoDB
- pymongo
- cryptography (Fernet / AES)
- hashlib

---

## 🔐 Security Design
- Master password is never stored in plaintext
- Encryption key derived from master password
- Stored credentials are encrypted at rest
- Passwords decrypted only after authentication

---

## ▶️ Run
```bash
pip install -r requirements.txt
python password_manager.py
