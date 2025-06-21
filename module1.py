import numpy as np
import requests
import json


from working.account import Login

# random 200 words generator
def typing_test_words():
    token = Login.is_authenticated()
    headers = {
        "Authorization":f"Bearer {token}",
    }
    try:
        res = requests.get("http://localhost:8000/user-info",headers = headers)
        print(res.text)
    except Exception as e:
        print(e)


    res_xp = json.loads(res.text).get("xp",0)
    print(res_xp,type(res_xp))

    with open("TestTypingWords","r") as word:
        rawlst = [i.split() for i in word]
        flatten_array = np.concatenate(rawlst)
        cleaned_array = np.array(
            list(map(lambda x: x.replace('.', '').replace(',', ''), flatten_array)))

        # number of random words
        size_word = 0
        if res_xp >= 100:
            size_word = 1000
        elif res_xp >= 70:
            size_word = 300
        elif res_xp >= 50:
            size_word = 100
        elif res_xp >= 30:
            size_word =50 
        elif res_xp >= 0:
            size_word = 30
        random_words = np.random.choice(cleaned_array, size=size_word)
        return " ".join(random_words)
