import requests, random

def predict_practice_word():
    words_in_string = requests.get("http://localhost:8000/practice-words")
    lst = words_in_string.json()
    ran = random.choices(lst,k = 50)
    # print("ran",ran)
    return " ".join(ran)
