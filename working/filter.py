import string
from working.account import Login
import requests
from datetime import datetime
import os
import json

class Tracker:
    def __init__(self, text, raw_char):
        self.text = text.lower().split()
        self.raw_char = raw_char

    def track_characters(self, target_char=None):
        typed = list(self.raw_char)
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

        # print("payload",payload)
        response = requests.post("http://localhost:8000/character-updated",headers = headers,json = payload)
        # print("save_char",response.json())


    def create_report(self,time):

        raw_user_char = 0
        for word in self.raw_char:
            raw_user_char += len(word)

        print("raw_user_char",raw_user_char)
        # rwpm
        rwpm = (raw_user_char / 5) / (time/60)
        print(rwpm)

        correct_char = 0
        for i in range(min(len(self.text),len(self.raw_char))):
            for j in range(min(len(self.text[i]),len(self.raw_char[i]))):
                if self.raw_char[i][j] == self.text[i][j]:
                    correct_char += 1

        print("correct_char",correct_char)
        
        #wpm
        wpm = (correct_char / 5) / (time/60)
        print(wpm)

        #accuracy
        accu = correct_char/raw_user_char * 100


        # save_report_db function should be called first be get session_name for file name
        print("call save db")
        response = self.save_report_db(rwpm,wpm,accu,time)

        file_path = response.get("file_path")


        self.save_to_file(raw_user_char,correct_char,file_path)

        return response


    def save_to_file(self,raw_user_char,correct_char,file_path):
        json_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "context_text": self.text,
            "user_text": self.raw_char,
            "raw_user_input_count": raw_user_char,
            "correct_char_count": correct_char,
            "mistakes": [
                {"position": i, "expected": self.text[i], "actual": self.raw_char[i]}
                for i in range(min(len(self.text), len(self.raw_char)))
                if self.text[i] != self.raw_char[i]
            ]
        }


        folder_path = "./report"
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
            with open(file_path,"w") as file:
                file.write(json.dumps(json_data))
                print("if",os.path.exists(file_path))
        else:
            with open(file_path,"w") as file:
                file.write(json.dumps(json_data))
                print("else",os.path.exists(file_path))
                print(os.path.abspath(file_path))



    def save_report_db(self,rwpm,wpm,accu,second):
        tk = Login.is_authenticated()
        headers = {
            "Authorization":f"Bearer {tk}",
            "Content-Type":"application/json"
        }
        js = {
            "wpm": wpm, 
            "rwpm": rwpm,
            "accuracy": accu,
            "second":second
        }

        response = requests.post("http://localhost:8000/create-report",headers = headers,json = js)
        # print("res",res.json())
        return response.json()


