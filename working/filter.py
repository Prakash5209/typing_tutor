import string
from working.account import Login
import requests

class Tracker:
    def __init__(self, text, raw_char):
        self.text = text.lower().split()
        self.raw_char = raw_char

    def track_characters(self, target_char=None):
        print("text",self.text)
        print("raw_char",self.raw_char)

        typed = list(self.raw_char)
        print(typed)
        self.char_dict = {key: [0,0] for key in string.ascii_lowercase}

        lst_text = list(map(lambda x:list(x),self.text))

        for i in range(len(self.raw_char)):
            if len(self.raw_char[i]) == len(lst_text[i]):
                for j in range(len(self.raw_char[i])):
                    if self.raw_char[i][j] != lst_text[i][j]:
                        self.char_dict[lst_text[i][j]][1] += 1
                        self.char_dict[self.raw_char[i][j]][0] += 1


            elif len(self.raw_char[i]) < len(lst_text[i]):
                for j in range(len(self.raw_char[i])):
                    if self.raw_char[i][j] != lst_text[i][j]:
                        self.char_dict[lst_text[i][j]][1] += 1
                        self.char_dict[self.raw_char[i][j]][0] += 1
                for k in range(1,(len(lst_text[i])-len(self.raw_char[i]))+1):
                    self.char_dict[lst_text[i][-k]][1] += 1


            elif len(self.raw_char[i]) > len(lst_text[i]):
                for j in range(len(lst_text[i])):
                    if self.raw_char[i][j] != lst_text[i][j]:
                        self.char_dict[lst_text[i][j]][1] += 1
                        self.char_dict[self.raw_char[i][j]][0] += 1
                for k in range(1,(len(self.raw_char[i])-len(lst_text[i]))+1):
                    self.char_dict[self.raw_char[i][-k]][0] += 1

        self.only_char = {k:j for k,j in self.char_dict.items() if j[0] > 0 or j[1] > 0}
        print(self.only_char)
        self.save_char(self.only_char)
        return self.only_char

    def save_char(self,chars: dict):
        login = Login.is_authenticated()

        headers = {
            "Authorization":f"Bearer {login}",
            "Content-Type":"application/json"
        }
        payload = {
            "jon":chars
        }
        response = requests.post("http://localhost:8000/character-updated",headers = headers,json = payload)
        print("response",response.status_code)

