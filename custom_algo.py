from sklearn.neighbors import NearestNeighbors
from typing import Dict,List
import numpy as np

class Suggest:
    error_map: Dict = None
    letter_scores: Dict = None

    # word_list = [
    #     # Example subset for brevity (you can use your full list here)
    #     "application", "banana", "candle", "keyboard", "toolkit", "apple",
    #     "kite", "lamp", "mom", "milk", "quiz", "jazz", "xylophone", "rainbow", "zipper"
    # ]
    

    word_list: List = []

    with open("words_alpha.txt","r") as word:
        re = word.read()
        lst = re.split()
        word_list = np.array([i for i in lst if len(i) <= 6])


    @classmethod
    def assign_mistake_keys(cls, dt: Dict):
        cls.error_map = dt
        cls.letter_scores = {k: sum(v) for k, v in dt.items()}

    @classmethod
    def get_top_mistake_letters(cls, n=5):
        return sorted(cls.letter_scores, key=cls.letter_scores.get, reverse=True)[:n]

    @staticmethod
    def word_to_vector(word: str, top_letters: set) -> np.ndarray:
        vec = np.zeros(26)
        for ch in set(word.lower()):
            if ch in top_letters:
                idx = ord(ch) - ord('a')
                vec[idx] = 1
        return vec

    @classmethod
    def predict_words(cls, n_neighbors=30, top_n_letters=5):
        if cls.letter_scores is None:
            raise ValueError("Letter scores not initialized. Call assign_mistake_keys() first.")

        top_letters = set(cls.get_top_mistake_letters(top_n_letters))

        print(f"Top mistake letters: {top_letters}")

        word_vectors = np.array([
            cls.word_to_vector(word, top_letters) for word in cls.word_list
        ])

        knn = NearestNeighbors(n_neighbors=min(n_neighbors, len(cls.word_list)), metric="cosine")
        knn.fit(word_vectors)

        # Create a target vector representing all top mistake letters
        target_vec = np.zeros(26)
        for ch in top_letters:
            target_vec[ord(ch) - ord('a')] = 1

        distances, indices = knn.kneighbors([target_vec])

        suggested_words = [cls.word_list[i] for i in indices[0]]

        # return suggested_words
        
        # randomize words
        randomize = np.random.choice(suggested_words,size=30)
        return randomize

