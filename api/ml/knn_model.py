from sklearn.neighbors import NearestNeighbors
import numpy as np


class Suggest:
    # 1. Mistake data
    error_map = {
        "a": [12, 16], "b": [0, 1], "c": [6, 6], "d": [7, 5], "e": [9, 15], "f": [2, 0],
        "g": [6, 8], "h": [3, 6], "i": [15, 17], "j": [0, 0], "k": [2, 1], "l": [6, 8],
        "m": [1, 5], "n": [12, 18], "o": [10, 11], "p": [4, 6], "q": [0, 0], "r": [2, 6],
        "s": [10, 14], "t": [16, 21], "u": [7, 9], "v": [4, 4], "w": [2, 1], "x": [0, 0],
        "y": [11, 11], "z": [0, 0]
    }

    letter_scores = {k: sum(v) for k, v in error_map.items()}

   
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
            "watermelon", "xylophone", "yacht", "zebra", "airplane", "basket", "caterpillar", "dragon",
            "envelope", "feather", "globe", "honey", "igloo", "jellyfish", "kangaroo", "lighthouse",
            "mushroom", "napkin", "octopus", "penguin", "quiver", "rainbow", "scissors", "telescope",
            "unicorn", "vulture", "whale", "xylophone", "yo-yo", "zipper", "anchor", "blossom",
            "compass", "dandelion", "eclipse", "flamingo", "giraffe", "harmonica", "iceberg", "jigsaw",
            "kaleidoscope", "lantern", "mermaid", "nectarine", "orchard", "peacock", "quicksand",
            
            # Hard words (60)
            "quintessential", "juxtaposition", "xenophobia", "zwieback", "acquiesce", "bureaucracy",
            "czar", "dyslexia", "euphoria", "fjord", "gazebo", "hygge", "ivory", "jazz", "kaleidoscope",
            "labyrinth", "mnemonic", "nymph", "onomatopoeia", "phoenix", "quasar", "rhetoric", "syzygy",
            "tsunami", "ubiquitous", "vortex", "wildebeest", "xenon", "yacht", "zeitgeist", "asymptote",
            "bouquet", "chrysanthemum", "dichotomy", "ephemeral", "facetious", "grandiose", "haphazard",
            "idiosyncrasy", "jeopardize", "kleptomania", "languorous", "mellifluous", "nomenclature",
            "obfuscate", "pandemonium", "quintuple", "recalcitrant", "serendipity", "thesaurus",
            "unambiguous", "verisimilitude", "whimsical", "xerography", "yesterday", "zoological",
            "ambidextrous", "belligerent", "circumlocution", "discombobulate", "extraterrestrial",
            
            # Words covering less common letters (20)
            "jazz", "quiz", "vixen", "wax", "jinx", "fuzz", "pyx", "qat", "vex", "zephyr",
            "junk", "quartz", "vibe", "wok", "jog", "quip", "vow", "wiz", "jolt", "quark"
        ]

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

    @classmethod
    def predict_words(cls):
        top_letters = set(cls.get_top_mistake_letters(7))
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
        print("filter_words",raw_suggested_words)


# Run the prediction
# Suggest.predict_words()

