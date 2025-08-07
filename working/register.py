import requests


class Register:
    def __init__(self, email, username, password, confirm_password):
        self.email = email
        self.username = username
        self.password = password
        self.confirm_password = confirm_password

    # register account
    def __register_new_account(self):
        if self.confirm_password == self.confirm_password:
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
        try:
            response = requests.post("http://localhost:8000/get-user/",
                                     json={"username": self.username, "password": self.password})
            return response
        except Exception as e:
            return e

    def makePayload(self):
        resp = self.get_user()
        return resp

    # def generateToken(self):
    #     en = jwt.encode(self.getPayload(), Login.secret, algorithm=["HS256"])
    #     print("token", en)
