from dotenv import load_dotenv
import re
import os
import requests
import jwt
import json
import datetime
from cryptography.fernet import Fernet
import smtplib
import string
from smtplib import SMTPException
import requests
import random
import json
import redis
from email.mime.text import MIMEText
from pathlib import Path


env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

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

        pattern = r'^(?=.*\d)(?=.*[!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]).{6,}$'

        if not re.fullmatch(pattern, self.password):
            print("Password must be at least 6 characters long, contain at least one digit and one punctuation mark.")
            return

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
    secret = os.getenv("JWT_SECRET_KEY")

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def get_user(self):

        if self.username and self.password:
            try:
                response = requests.post("http://localhost:8000/get-user/",
                                         json={"username": self.username, "password": self.password})
                # print("response", response)
                response_text = json.loads(response.text)

                if response_text and response.status_code == 200:
                    self.generateToken(response_text.get('id'), response_text.get('username'))
                return response
            except Exception as e:
                print("get_user Exception", e)
        else:
            print("username and password input is empty")

    def generateToken(self, id, username):
        payload = {
            "id": id,
            "username": username,
            # "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours = 24),
            "iat": datetime.datetime.utcnow()
        }

        try:
            encoded = jwt.encode(payload, Login.secret, algorithm="HS256")
            # print("encoded",encoded)
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

                authenticted_or_not = token_exp_time > datetime.datetime.utcnow()
                if authenticted_or_not:
                    return decrypted
                else:
                    with open(CREDENTIAL_FILE,"w") as file:
                        file.write("")
                        print("removed token")
                return "token expired"
        except jwt.ExpiredSignatureError:
            print("Token has expired.")
            return False
        except Exception as e:
            print("is_authenticated Exception:", e)
            return False


class UserInfo:
    @staticmethod
    def get_userinfo():
        try:
            if not os.path.exists(CREDENTIAL_FILE):
                print("no credentials file found")
                return False
            with open(CREDENTIAL_FILE,"rb") as file:
                encrypted = file.read()
                decrypted = cipher_suite.decrypt(encrypted).decode()
                token = jwt.decode(decrypted,Login.secret,algorithms=["HS256"])
                if Login.is_authenticated():
                    return token

        except Exception as e:
            print("get_userinfo",e)




class Account_recovery:
    r = redis.Redis(host="localhost", port=6379)

    def __init__(self, usename: str):
        self.username: str = usename

    def request_email(self) -> str:
        try:
            response = requests.post("http://localhost:8000/get-email/", json={
                "username": self.username
            })
            self.email = json.loads(response.text)
            return self.email
        except Exception as e:
            print("send_mail_to_this_user", e)
            return ""

    def generate_code(self):
        chars = string.ascii_letters + string.digits
        existing_code = {Account_recovery.r.get(
            key).decode() for key in Account_recovery.r.scan_iter("*") if Account_recovery.r.get(key)}

        while True:
            code = "".join(random.choices(chars, k=6))
            if code not in existing_code:
                return code

    def send_mail(self):
        sender_email = os.getenv("SENDER_EMAIL")
        sender_email_password = os.getenv("SENDER_PASSWORD")

        self.email = self.request_email()
        if not self.email:
            print("invalid email response")
            return

        # generate and store code in redis
        self.code = self.generate_code()
        Account_recovery.r.setex(self.email, 300, self.code)

        try:
            msg = MIMEText(
                f'This code "{self.code}" is valid for 5 minutes only')
            msg["Subject"] = "typing tutor account recovery"
            msg["From"] = sender_email
            msg["To"] = self.email

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, sender_email_password)
                server.send_message(msg)

            print("email sent successfully")

        except SMTPException as e:
            print("smtp error: ", e)


class Verification_code:

    def confirm_recovery_code(self, code):
        try:
            dt = {Account_recovery.r.get(
                key).decode(): key.decode() for key in Account_recovery.r.scan_iter("*")}
            if dt:
                self.email = dt.get(code)
                return dt.get(code)
            else:
                return False
        except Exception as e:
            print(e)

    # create new password
    def create_new_password(self, email, new_password, confirm_password):
        if new_password == confirm_password:
            try:
                response = requests.post("http://localhost:8000/reset-password/", json={
                    "email": email,
                    "password": confirm_password
                })
            except Exception as e:
                print(e)

            res = json.loads(response.text)
            # print(res)
            # print("new password", email, new_password, confirm_password)


class Logout:
    def remove_token(self):
        with open(CREDENTIAL_FILE,"w") as file:
            file.write("")
            print("removed token")
            print("logged out")
