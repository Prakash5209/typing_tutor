import requests

from working.account import Login
from custom_algo import Suggest

class Handler_algo:
    def __init__(self):
        self.mistakes = self.get_mistake()


    def get_mistake(self):
        tk = Login.is_authenticated()
        headers = {
            "Authorization":f"Bearer {tk}"
        }
        response = requests.get("http://localhost:8000/get-mistakes",headers = headers)
        mistakes = response.json()
        return mistakes

    def predict_words(self):
        self.hand = Suggest.assign_mistake_keys(self.mistakes)
        # print(Suggest.error_map,Suggest.letter_scores)
        # print(Suggest.predict_words())
        return " ".join(Suggest.predict_words())
