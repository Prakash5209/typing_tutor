from sklearn.neighbors import NearestNeighbors
from typing import Dict
import numpy as np
import requests

from working.account import Login

class Suggest:
    error_map: Dict = None
    letter_scores: Dict = None

    word_list = [
        # Original words (20)
        "application", "banana", "candle", "network", "toolkit", "keyboard", "typo",
        "mistake", "random", "frequency", "input", "function", "approach", "python",
        "statistics", "attention", "performance", "instruction", "machine", "learning",
        # Easy words (100)
        "apple", "book", "cat", "dog", "egg", "fish", "goat", "hat", "ice", "jump",
        "kite", "lamp", "moon", "nest", "open", "pig", "queen", "red", "sun", "tree",
        "umbrella", "van", "water", "box", "yellow", "zoo", "ant", "ball", "car", "duck",
        "ear", "fox", "girl", "hand", "ink", "jam", "king", "leg", "mom", "nut",
        "apple", "baby", "cake", "door", "eye", "frog", "game", "hill", "iron", "jet",
        "kiss", "love", "milk", "nose", "owl", "pie", "quilt", "rain", "star", "toy",
        "up", "vet", "wolf", "xray", "yarn", "zip", "arm", "bus", "cow", "dig",
        "elf", "gap", "hop", "jug", "kid", "log", "mat", "net", "old", "pen",
        "quail", "rug", "sock", "tap", "urn", "vat", "web", "yell", "zap", "art",
        "bat", "cup", "dot", "fan", "gum", "hen", "ill", "job", "kit", "lip",
        
            # Medium words (80)
        "bicycle", "dolphin", "garden", "jacket", "kitten", "ladder", "mirror", "notebook",
        "orange", "puzzle", "rabbit", "soccer", "turtle", "violin", "window", "xylophone",
        "yogurt", "zeebra", "acorn", "butter", "camera", "diamond", "elephant", "firefly",
        "guitar", "hamburger", "island", "jungle", "koala", "lemon", "mountain", "necklace",
        "ocean", "parrot", "quilt", "rocket", "sandwich", "telephone", "umbrella", "volcano",
        "envelope", "feather", "globe", "honey", "igloo", "jellyfish", "kangaroo", "lighthouse",
        "watermelon", "xylophone", "yacht", "zebra", "airplane", "basket", "caterpillar", "dragon",
        "mushroom", "napkin", "octopus", "penguin", "quiver", "rainbow", "scissors", "telescope",
        "unicorn", "vulture", "whale", "xylophone", "yo-yo", "zipper", "anchor", "blossom",
        "compass", "dandelion", "eclipse", "flamingo", "giraffe", "harmonica", "iceberg", "jigsaw",
        "kaleidoscope", "lantern", "mermaid", "nectarine", "orchard", "peacock", "quicksand",
        
        
        # Words covering less common letters (20)
        "jazz", "quiz", "vixen", "wax", "jinx", "fuzz", "pyx", "qat", "vex", "zephyr",
        "junk", "quartz", "vibe", "wok", "jog", "quip", "vow", "wiz", "jolt", "quark"
    ]


    @classmethod
    def assign_mistake_keys(cls,dt: Dict):
        cls.error_map = dt
        cls.letter_scores = {k: sum(v) for k, v in dt.items()}


    @classmethod
    def get_top_mistake_letters(cls, n=7):
        return sorted(cls.letter_scores, key=cls.letter_scores.get, reverse=True)[:n]

    @staticmethod
    def word_to_vector(word: str, top_letters: set) -> np.ndarray:
        vec = np.zeros(26)
        for ch in set(word.lower()):
            if ch in top_letters:
                idx = ord(ch) - ord('a')
                vec[idx] = 1
        return vec



    # @classmethod
    # def predict_words(cls):
    #     top_letters = set(cls.get_top_mistake_letters(5))
    #     print("Top mistake letters:", top_letters)
    # 
    #     short_words = [word for word in cls.word_list if len(word) <= 6]
    # 
    #     # Filter and only keep words that match at least one top letter
    #     filtered_words = []
    #     filtered_vectors = []
    # 
    #     for word in short_words:
    #         vec = cls.word_to_vector(word, top_letters)
    #         if vec.sum() > 0:
    #             filtered_words.append(word)
    #             filtered_vectors.append(vec)
    # 
    #     if not filtered_words:
    #         return []
    # 
    #     word_vectors = np.array(filtered_vectors)
    # 
    #     knn = NearestNeighbors(n_neighbors=min(100, len(filtered_words)), metric="cosine")
    #     knn.fit(word_vectors)
    # 
    #     target_vec = np.zeros(26)
    #     for ch in top_letters:
    #         target_vec[ord(ch) - ord('a')] = 1
    # 
    #     distances, indices = knn.kneighbors([target_vec])
    # 
    #     # print("Suggested Words (Length <= 6):")
    #     suggested_words = [filtered_words[i] for i in indices[0]]
    #     return suggested_words

    @classmethod
    def predict_words(cls):
        top_letters = set(cls.get_top_mistake_letters(5))
        word_vectors = np.array([
            cls.word_to_vector(word, top_letters) for word in cls.word_list
        ])

        knn = NearestNeighbors(n_neighbors=100, metric="cosine")
        knn.fit(word_vectors)

        # Synthetic vector with all top mistake letters
        target_vec = np.zeros(26)
        for ch in top_letters:
            target_vec[ord(ch) - ord('a')] = 1

        distances, indices = knn.kneighbors([target_vec])

        print("Suggested Words (KNN based on High Mistake Letters):")
        raw_suggested_words = [cls.word_list[i] for i in indices[0]]
        # filter_words = [i for i in raw_suggested_words if len(i) <= 5]
        # print("filter_words",raw_suggested_words)
        raw_suggested_words = [cls.word_list[i] for i in indices[0]]
        return " ".join(raw_suggested_words)
        # return raw_suggested_words

        # filtered_words = [word for word in raw_suggested_words if len(word) <= 6]
        # return filtered_words


# Run the prediction
# Suggest.predict_words()

