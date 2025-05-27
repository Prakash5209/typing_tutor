import os
import requests
import random
import jwt
import datetime
from dotenv import load_dotenv
from pathlib import Path
from cryptography.fernet import Fernet

# Load environment variables explicitly
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Paths setup
CURRENT_FILE_PATH = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_FILE_PATH)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
CREDENTIAL_FILE = os.path.join(PROJECT_ROOT, ".credential")
FERNET_KEY_FILE = os.path.join(PROJECT_ROOT, ".fernet_key")

def load_fernet_key():
    if os.path.exists(FERNET_KEY_FILE):
        with open(FERNET_KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(FERNET_KEY_FILE, "wb") as f:
            f.write(key)
        return key

cipher_suite = Fernet(load_fernet_key())

print("Credential file path:", CREDENTIAL_FILE)  # For debugging

def predict_practice_word():
    response = requests.get("http://localhost:8000/practice-words")
    response.raise_for_status()  # Raise if HTTP error occurs
    words_list = response.json()
    random_words = random.choices(words_list, k=50)
    print("random_words",random_words)
    return " ".join(random_words)

class Knn_handler:
    @staticmethod

    def test():
        print("okay")
