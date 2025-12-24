import hashlib
import base64
import getpass
from cryptography.fernet import Fernet
from pymongo import MongoClient

# ---------------- DATABASE ----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["password_manager"]
creds = db["credentials"]
users = db["users"]

creds.create_index("service", unique=True)

# ---------------- SECURITY ----------------
def hash_master_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def derive_key(master_password: str) -> bytes:
    hashed = hashlib.sha256(master_password.encode()).digest()
    return base64.urlsafe_b64encode(hashed)

# ---------------- AUTH ----------------
def setup_master_password():
    print("🔐 Setup Master Password")
    pwd = getpass.getpass("Create Master Password: ")
    confirm = getpass.getpass("Confirm Master Password: ")

    if pwd != confirm:
        print("❌ Passwords do not match")
        exit()

    users.insert_one({"master_hash": hash_master_password(pwd)})
    print("✅ Master password set")

def authenticate():
    if users.count_documents({}) == 0:
        setup_master_password()

    stored = users.find_one()
    pwd = getpass.getpass("Enter Master Password: ")

    if hash_master_password(pwd) != stored["master_hash"]:
        print("❌ Authentication failed")
        exit()

    return Fernet(derive_key(pwd))

# ---------------- CRUD ----------------
def add_password(fernet):
    service = input("Service: ").strip()
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")

    encrypted = fernet.encrypt(password.encode())

    try:
        creds.insert_one({
            "service": service,
            "username": username,
            "password": encrypted
        })
        print("✅ Password stored securely")
    except:
        print("❌ Service already exists")

def view_password(fernet):
    service = input("Service: ").strip()
    record = creds.find_one({"service": service})

    if not record:
        print("❌ Not found")
        return

    decrypted = fernet.decrypt(record["password"]).decode()
    print(f"""
🔐 Credential
Service  : {record['service']}
Username : {record['username']}
Password : {decrypted}
""")

def update_password(fernet):
    service = input("Service: ").strip()
    new_pwd = getpass.getpass("New Password: ")
    encrypted = fernet.encrypt(new_pwd.encode())

    result = creds.update_one(
        {"service": service},
        {"$set": {"password": encrypted}}
    )

    print("✅ Updated" if result.matched_count else "❌ Not found")

def delete_password():
    service = input("Service: ").strip()
    result = creds.delete_one({"service": service})
    print("✅ Deleted" if result.deleted_count else "❌ Not found")

def list_services():
    print("\n📋 Services:")
    for s in creds.find({}, {"service": 1, "_id": 0}):
        print("-", s["service"])

# ---------------- CLI ----------------
def menu():
    fernet = authenticate()

    while True:
        print("""
=============================
 REAL PASSWORD MANAGER
=============================
1. Add Password
2. View Password
3. Update Password
4. Delete Password
5. List Services
6. Exit
""")

        choice = input("Choose: ")

        if choice == "1":
            add_password(fernet)
        elif choice == "2":
            view_password(fernet)
        elif choice == "3":
            update_password(fernet)
        elif choice == "4":
            delete_password()
        elif choice == "5":
            list_services()
        elif choice == "6":
            print("👋 Goodbye")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    menu()
