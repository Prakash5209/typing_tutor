import smtplib
import string
from smtplib import SMTPException
import requests
import random
import json
import redis
from email.mime.text import MIMEText


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
        sender_email = "prakashkchaudhary5209@gmail.com"
        sender_email_password = "kbgb betb fvxf qxbg"

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
        dt = {Account_recovery.r.get(
            key).decode(): key.decode() for key in Account_recovery.r.scan_iter("*")}
        print(dt.get(code))
