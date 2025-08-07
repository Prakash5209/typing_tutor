import Levenshtein
import string
from working.account import Login
import requests
from datetime import datetime
import os
import json

class Tracker:
    def __init__(self, text, raw_char:list):
        self.text = text.lower().split()
        self.raw_char = raw_char

    def track_characters(self, target_char=None):
        typed = self.raw_char
        self.char_dict = {key: [0,0] for key in string.ascii_lowercase}

        lst_text = list(map(lambda x:list(x),self.text))

        for i in range(len(self.raw_char)):
            if len(self.raw_char[i]) == len(lst_text[i]):
                for j in range(len(self.raw_char[i])):
                    if self.raw_char[i][j] != lst_text[i][j]:
                        self.char_dict[lst_text[i][j]][1] += 1
                        try:
                            self.char_dict[self.raw_char[i][j]][0] += 1
                        except KeyError:
                            # capital key error
                            if self.raw_char[i][j] in list(string.ascii_letters):
                                lower_char = self.raw_char[i][j].lower()
                                self.char_dict[lower_char][0] += 1
                            else:
                                print("string.punctuation")
                        except Exception as e:
                            print(e);


            elif len(self.raw_char[i]) < len(lst_text[i]):
                for j in range(len(self.raw_char[i])):
                    if self.raw_char[i][j] != lst_text[i][j]:
                        self.char_dict[lst_text[i][j]][1] += 1
                        try:
                            self.char_dict[self.raw_char[i][j]][0] += 1
                        except KeyError:
                            # capital key error
                            if self.raw_char[i][j] in list(string.ascii_letters):
                                lower_char = self.raw_char[i][j].lower()
                                self.char_dict[lower_char][0] += 1
                            else:
                                print("string.punctuation")
                        except Exception as e:
                            print(e);

                for k in range(1,(len(lst_text[i])-len(self.raw_char[i]))+1):
                    try:
                        self.char_dict[self.raw_char[i][-k]][0] += 1
                    except Exception as e:
                        # ignore all the punctuation keyerror
                        print(e)



            elif len(self.raw_char[i]) > len(lst_text[i]):
                for j in range(len(lst_text[i])):
                    if self.raw_char[i][j] != lst_text[i][j]:
                        self.char_dict[lst_text[i][j]][1] += 1
                        try:
                            self.char_dict[self.raw_char[i][j]][0] += 1
                        except KeyError:
                            # capital key error
                            if self.raw_char[i][j] in list(string.ascii_letters):
                                lower_char = self.raw_char[i][j].lower()
                                self.char_dict[lower_char][0] += 1
                            else:
                                print("string.punctuation")
                        except Exception as e:
                            print(e);

                for k in range(1,(len(self.raw_char[i])-len(lst_text[i]))+1):
                    try:
                        self.char_dict[self.raw_char[i][-k]][0] += 1
                    except Exception as e:
                        # ignore all the punctuation keyerror
                        print(e)


        self.only_char = {k:j for k,j in self.char_dict.items() if j[0] > 0 or j[1] > 0}
        self.except_char = self.filter_mistake_tracker()
        self.save_char(self.only_char,self.except_char)

        return self.only_char

    def save_char(self,chars: dict,no_chars: dict):
        login = Login.is_authenticated()

        headers = {
            "Authorization":f"Bearer {login}",
            "Content-Type":"application/json"
        }
        payload = {
            "jon":chars,
            "no_jon":no_chars
        }

        # print("payload",payload)
        response = requests.post("http://localhost:8000/character-updated",headers = headers,json = payload)
        # print("save_char",response.json())


    def create_report(self,time):

        raw_user_char = 0
        for word in self.raw_char:
            raw_user_char += len(word)

        # rwpm
        rwpm = (raw_user_char / 5) / (time/60)

        correct_char = 0
        for i in range(min(len(self.text),len(self.raw_char))):
            for j in range(min(len(self.text[i]),len(self.raw_char[i]))):
                if self.raw_char[i][j] == self.text[i][j]:
                    correct_char += 1

        #wpm
        wpm = (correct_char / 5) / (time/60)

        print("rwpm",raw_user_char)
        print("wpm",correct_char)

        #accuracy
        # accu = (correct_char/raw_user_char) * 100
        typed = " ".join(self.raw_char)
        target = " ".join(self.text[:len(self.raw_char)])

        print("typed",typed)
        print("target",target)

        distance = Levenshtein.distance(target,typed)
        accuracy = ((len(target) - distance) / len(target)) * 100
        print("accu",accuracy)


        # save_report_db function should be called first be get session_name for file name
        response = self.save_report_db(rwpm,wpm,accuracy,time)


        # updating the xp
        login = Login.is_authenticated()
        headers = {

            "Authorization":f"Bearer {login}",
            "Content-Type":"application/json"
        }

        get_xp = requests.get("http://localhost:8000/user-info",headers = headers)
        self.instance_xp = json.loads(get_xp.text).get("xp")

        self.total_xp = 0
        self.wpm_xp = 0
        self.accuracy_xp = 0

        wpm_thresholds = [(100, 5), (80, 4), (60, 3), (40, 2), (20, 1), (1, 0.1)]
        # acc_thresholds = [(100,3), (80,2.4), (60,1.8), (40,1.2), (20,0.6), (1,0.3)]
        acc_thresholds = [(100,3), (80,2.4), (60,1.8), (40,1.2), (20,-1.5), (1,-0.5)]
        for threshold, xp in wpm_thresholds:
            if wpm >= threshold:
                self.wpm_xp += xp
                break
        else:
            self.wpm_xp += 0

        for threshold, xp in acc_thresholds:
            if accuracy >= threshold:
                self.accuracy_xp += xp
                break
        else:
            self.accuracy_xp += 0

        self.total_xp = self.wpm_xp + self.accuracy_xp + self.instance_xp

        print(self.accuracy_xp)
        print(self.wpm_xp)
        print(self.total_xp)
        payload = {
            "xp":self.total_xp
        }
        if self.total_xp > 0:
            xp_response = requests.patch("http://localhost:8000/update-xp",headers = headers,json = payload)
            print("xp_response",xp_response)


        file_path = response.get("file_path")


        self.save_to_file(raw_user_char,correct_char,file_path)
        self.filter_mistake_tracker()
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
        else:
            with open(file_path,"w") as file:
                file.write(json.dumps(json_data))



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
        print("js",js)
        response = requests.post("http://localhost:8000/create-report",headers = headers,json = js)
        return response.json()


    def filter_mistake_tracker(self):
        dt = {i:0 for i in string.ascii_lowercase} 
        no_only_char = {i:dt[i]+1 if i not in self.only_char else dt[i] for i in dt}
        return no_only_char

