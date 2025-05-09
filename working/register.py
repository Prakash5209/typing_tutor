import requests


class Register:

    def __init__(self, email, username, password, confirm_password):
        self.email = email
        self.username = username
        self.password = password
        self.confirm_password = confirm_password

    # register account
    def register_new_account(self):
        if self.confirm_password == self.confirm_password:
            try:
                test_response = requests.post("http://localhost:8000/create-user/",
                                              json={
                                                  'email': self.email,
                                                  'username': self.username,
                                                  'password': self.password
                                              })
            except Exception as e:
                print(e)
            print("response", test_response)
