
import os
import requests
import jwt
import json
import datetime
from cryptography.fernet import Fernet

# -- Secure location for token and key files
CREDENTIAL_FILE = ".credential"
FERNET_KEY_FILE = ".fernet_key"

# -- Load or generate Fernet key


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


class Register:
    def __init__(self, email, username, password, confirm_password):
        self.email = email
        self.username = username
        self.password = password
        self.confirm_password = confirm_password

    def __register_new_account(self):
        if self.confirm_password == self.password:
            try:
                test_response = requests.post("http://localhost:8000/create-user/",
                                              json={
                                                  'email': self.email,
                                                  'username': self.username,
                                                  'password': self.password
                                              })
                return test_response.status_code
            except Exception as e:
                print(e)


class Login:
    secret = "prakashchaudhary"

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_user(self):
        print("username", self.username)
        print("password", self.password)

        if self.username and self.password:
            try:
                response = requests.post("http://localhost:8000/get-user/",
                                         json={"username": self.username, "password": self.password})
                print("response", response)
                response_text = json.loads(response.text)

                if response_text:
                    self.generateToken(response_text.get(
                        'id'), response_text.get('username'))
                return response
            except Exception as e:
                print("get_user Exception", e)
        else:
            print("username and password input is empty")

    def generateToken(self, id, username):
        payload = {
            "id": id,
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            "iat": datetime.datetime.utcnow()
        }

        try:
            encoded = jwt.encode(payload, Login.secret, algorithm="HS256")
            self.save_token(encoded)
        except Exception as e:
            print("generateToken Exception", e)

    def save_token(self, encoded_token):
        try:
            with open(CREDENTIAL_FILE, "wb") as file:
                encrypted = cipher_suite.encrypt(encoded_token.encode())
                file.write(encrypted)
            print("Token saved successfully.")
        except Exception as e:
            print("save_token Exception", e)

    @staticmethod
    def is_authenticated():
        try:
            if not os.path.exists(CREDENTIAL_FILE):
                print("No credentials file found.")
                return False

            with open(CREDENTIAL_FILE, "rb") as file:
                encrypted = file.read()
                decrypted = cipher_suite.decrypt(encrypted).decode()

                token = jwt.decode(decrypted, Login.secret,
                                   algorithms=["HS256"])
                token_exp_time = datetime.datetime.utcfromtimestamp(
                    token["exp"])
                print("Token expiration:", token_exp_time)

                return token_exp_time > datetime.datetime.utcnow()
        except jwt.ExpiredSignatureError:
            print("Token has expired.")
            return False
        except Exception as e:
            print("is_authenticated Exception:", e)
            return False
