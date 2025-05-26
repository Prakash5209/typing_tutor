from sklearn.neighbors import NearestNeighbors
import numpy as np
import requests


class Suggest:
    # 1. Mistake data
    error_map = {"a": [3, 3], "b": [0, 0], "c": [0, 0], "d": [0, 0], "e": [0, 0], "f": [0, 0], "g": [0, 0], "h": [0, 0], "i": [3, 1], "j": [0, 0], "k": [0, 0], "l": [0, 0], "m": [0, 0], "n": [0, 0], "o": [0, 0], "p": [0, 0], "q": [0, 0], "r": [0, 0], "s": [0, 0], "t": [0, 2], "u": [0, 0], "v": [0, 0], "w": [0, 0], "x": [0, 0], "y": [0, 0], "z": [0, 0]}

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
        "envelope", "feather", "globe", "honey", "igloo", "jellyfish", "kangaroo", "lighthouse",
        "watermelon", "xylophone", "yacht", "zebra", "airplane", "basket", "caterpillar", "dragon",
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
    ]+['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'the', 'lazy', 'dog', 'this', 'sentence', 'contains', 'every', 'letter', 'the', 'alphabet', 'and', 'often', 'used', 'for', 'typing', 'practice', 'typing', 'essential', 'skill', 'todays', 'digital', 'world', 'and', 'improving', 'your', 'speed', 'and', 'accuracy', 'can', 'greatly', 'enhance', 'your', 'productivity', 'whether', 'youre', 'student', 'professional', 'just', 'someone', 'who', 'enjoys', 'spending', 'time', 'the', 'computer', 'being', 'able', 'type', 'quickly', 'and', 'accurately', 'valuable', 'skill', 'practice', 'makes', 'perfect', 'and', 'the', 'more', 'you', 'type', 'the', 'better', 'youll', 'become', 'start', 'focusing', 'accuracy', 'and', 'then', 'gradually', 'increase', 'your', 'speed', 'there', 'are', 'many', 'online', 'resources', 'and', 'typing', 'tests', 'available', 'that', 'can', 'help', 'you', 'track', 'your', 'progress', 'some', 'popular', 'typing', 'test', 'websites', 'include', 'typingcom', 'fastfingers', 'and', 'keybr', 'these', 'platforms', 'offer', 'variety', 'exercises', 'and', 'tests', 'help', 'you', 'improve', 'your', 'typing', 'skills', 'when', 'practicing', 'its', 'important', 'maintain', 'proper', 'posture', 'and', 'hand', 'positioning', 'sit', 'straight', 'keep', 'your', 'feet', 'flat', 'the', 'floor', 'and', 'position', 'your', 'hands', 'that', 'your', 'fingers', 'are', 'resting', 'the', 'home', 'row', 'keys', 'the', 'home', 'row', 'keys', 'are', 'the', 'middle', 'row', 'letters', 'the', 'keyboard', 'asdf', 'for', 'the', 'left', 'hand', 'and', 'for', 'the', 'right', 'hand', 'your', 'thumbs', 'should', 'rest', 'lightly', 'the', 'space', 'bar', 'you', 'type', 'try', 'keep', 'your', 'eyes', 'the', 'screen', 'rather', 'than', 'down', 'the', 'keyboard', 'this', 'will', 'help', 'you', 'develop', 'muscle', 'memory', 'and', 'improve', 'your', 'typing', 'speed', 'may', 'feel', 'challenging', 'first', 'but', 'with', 'consistent', 'practice', 'youll', 'find', 'that', 'you', 'can', 'type', 'without', 'looking', 'the', 'keys', 'addition', 'practicing', 'regularly', 'its', 'also', 'helpful', 'take', 'breaks', 'and', 'stretch', 'your', 'hands', 'and', 'fingers', 'typing', 'for', 'long', 'periods', 'time', 'can', 'lead', 'fatigue', 'and', 'discomfort', 'sure', 'give', 'your', 'hands', 'rest', 'every', 'now', 'and', 'then', 'world', 'and', 'improving', 'your', 'speed', 'and', 'accuracy', 'can', 'greatly', 'enhance', 'your', 'productivity', 'whether', 'youre', 'student', 'professional', 'just', 'someone', 'who', 'enjoys', 'spending', 'time', 'the', 'computer', 'being', 'able', 'type', 'quickly', 'and', 'accurately', 'valuable', 'skill', 'practice', 'makes', 'perfect', 'and', 'the', 'more', 'you', 'type', 'the', 'better', 'youll', 'become', 'start', 'focusing', 'accuracy', 'and', 'then', 'gradually', 'increase', 'your', 'speed', 'there', 'are', 'many', 'online', 'resources', 'and', 'typing', 'tests', 'available', 'that', 'can', 'help', 'you', 'track', 'your', 'progress', 'some', 'popular', 'typing', 'test', 'websites', 'include', 'typingcom', 'fastfingers', 'and', 'keybr', 'these', 'platforms', 'offer', 'variety', 'exercises', 'and', 'tests', 'help', 'you', 'improve', 'your', 'typing', 'skills', 'when', 'practicing', 'its', 'important', 'maintain', 'proper', 'posture', 'and', 'hand', 'positioning', 'sit', 'straight', 'keep', 'your', 'feet', 'flat', 'the', 'floor', 'and', 'position', 'your', 'hands', 'that', 'your', 'fingers', 'are', 'resting', 'the', 'home', 'row', 'keys', 'the', 'home', 'row', 'keys', 'are', 'the', 'middle', 'row', 'letters', 'the', 'keyboard', 'asdf', 'for', 'the', 'left', 'hand', 'and', 'jkl', 'for', 'the', 'right', 'hand', 'your', 'thumbs', 'should', 'rest', 'lightly', 'the', 'space', 'bar', 'you', 'type', 'try', 'keep', 'your', 'eyes', 'the', 'screen', 'rather', 'than', 'looking', 'down', 'the', 'keyboard', 'this', 'will', 'help', 'you', 'develop', 'muscle', 'memory', 'and', 'improve', 'your', 'typing', 'speed', 'may', 'feel', 'challenging', 'first', 'but', 'with', 'consistent', 'practice', 'youll', 'find', 'that', 'you', 'can', 'type', 'without', 'looking', 'the', 'keys', 'addition', 'practicing', 'regularly', 'its', 'also', 'helpful', 'take', 'breaks', 'and', 'stretch', 'your', 'hands', 'and', 'fingers', 'typing', 'for', 'long', 'periods', 'time', 'can', 'lead', 'fatigue', 'and', 'discomfort', 'sure', 'give', 'your', 'hands', 'rest', 'every', 'now', 'and', 'then', 'stretching', 'exercises', 'such', 'spreading', 'your', 'fingers', 'wide', 'and', 'then', 'making', 'fist', 'can', 'help', 'relieve', 'tension', 'and', 'prevent', 'strain', 'another', 'tip', 'for', 'improving', 'your', 'typing', 'skills', 'use', 'all', 'ten', 'fingers', 'many', 'people', 'type', 'using', 'only', 'few', 'fingers', 'which', 'can', 'slow', 'them', 'down', 'and', 'lead', 'errors', 'using', 'all', 'ten', 'fingers', 'you', 'can', 'distribute', 'the', 'workload', 'more', 'evenly', 'and', 'type', 'more', 'efficiently', 'there', 'are', 'many', 'online', 'tutorials', 'and', 'guides', 'that', 'can', 'teach', 'you', 'proper', 'finger', 'placement', 'and', 'typing', 'techniques', 'you', 'continue', 'practice', 'youll', 'likely', 'notice', 'that', 'your', 'typing', 'speed', 'and', 'accuracy', 'improve', 'over', 'time', 'its', 'important', 'set', 'realistic', 'goals', 'and', 'track', 'your', 'progress', 'for', 'example', 'you', 'might', 'aim', 'increase', 'your', 'typing', 'speed', 'words', 'per', 'minute', 'each', 'week', 'keep', 'mind', 'that', 'everyone', 'progresses', 'their', 'own', 'pace', 'dont', 'get', 'discouraged', 'you', 'dont', 'see', 'immediate', 'results', 'addition', 'practicing', 'with', 'typing', 'tests', 'you', 'can', 'also', 'improve', 'your', 'skills', 'typing', 'real', 'world', 'content', 'for', 'example', 'you', 'might', 'try', 'typing', 'out', 'articles', 'essays', 'even', 'your', 'own', 'thoughts', 'and', 'ideas', 'this', 'will', 'help', 'you', 'get', 'used', 'typing', 'different', 'types', 'text', 'and', 'improve', 'your', 'overall', 'fluency', 'another', 'way', 'enhance', 'your', 'typing', 'skills', 'learn', 'keyboard', 'shortcuts', 'keyboard', 'shortcuts', 'are', 'combinations', 'keys', 'that', 'perform', 'specific', 'functions', 'such', 'copying', 'pasting', 'saving', 'document', 'memorizing', 'and', 'using', 'these', 'shortcuts', 'you', 'can', 'save', 'time', 'and', 'work', 'more', 'efficiently', 'some', 'common', 'keyboard', 'shortcuts', 'include', 'c', 'for', 'copy', 'for', 'paste', 'and', 's', 'for', 'save', 'its', 'also', 'important', 'stay', 'motivated', 'and', 'have', 'fun', 'while', 'practicing', 'typing', 'can', 'sometimes', 'feel', 'repetitive', 'try', 'mix', 'things', 'using', 'different', 'typing', 'games', 'and', 'challenges', 'many', 'typing', 'websites', 'offer', 'games', 'that', 'make', 'practice', 'more', 'enjoyable', 'and', 'engaging', 'for', 'example', 'you', 'might', 'try', 'game', 'where', 'you', 'have', 'type', 'words', 'they', 'fall', 'from', 'the', 'top', 'the', 'screen', 'race', 'against', 'the', 'clock', 'see', 'how', 'many', 'words', 'you', 'can', 'type', 'minute', 'conclusion', 'typing', 'valuable', 'skill', 'that', 'can', 'benefit', 'you', 'many', 'areas', 'life', 'whether', 'youre', 'typing', 'email', 'writing', 'report', 'chatting', 'with', 'friends', 'being', 'able', 'type', 'quickly', 'and', 'accurately', 'can', 'save', 'you', 'time', 'and', 'make', 'your', 'work', 'more', 'efficient', 'practicing', 'regularly', 'maintaining', 'proper', 'posture', 'and', 'using', 'all', 'ten', 'fingers', 'you', 'can', 'improve', 'your', 'typing', 'skills', 'and', 'become', 'more', 'confident', 'typist', 'remember', 'set', 'realistic', 'goals', 'track', 'your', 'progress', 'and', 'have', 'fun', 'along', 'the', 'way', 'with', 'dedication', 'and', 'persistence', 'youll', 'typing', 'like', 'pro', 'time', 'the', 'quick', 'brown', 'fox', 'jumps', 'over', 'the', 'lazy', 'dog', 'this', 'sentence', 'contains', 'every', 'letter', 'the', 'alphabet', 'and', 'often', 'used', 'for', 'typing', 'practice', 'typing', 'essential', 'skill', 'todays', 'digital', 'world', 'and', 'improving', 'your', 'speed', 'and', 'accuracy', 'can', 'greatly', 'enhance', 'your', 'productivity', 'whether', 'youre', 'student', 'professional', 'just', 'someone', 'who', 'enjoys', 'spending', 'time', 'the', 'computer', 'being', 'able', 'type', 'quickly', 'and', 'accurately', 'valuable', 'skill', 'practice', 'makes', 'perfect', 'and', 'the', 'more', 'you', 'type', 'the', 'better', 'youll', 'become', 'start', 'focusing', 'accuracy', 'and', 'then', 'gradually', 'increase', 'your', 'speed', 'there', 'are', 'many', 'online', 'resources', 'and', 'typing', 'tests', 'available', 'that', 'can', 'help', 'you', 'track', 'your', 'progress', 'some', 'popular', 'typing', 'test', 'websites', 'include', 'typingcom', 'fastfingers', 'and', 'keybr', 'these', 'platforms', 'offer', 'variety', 'exercises', 'and', 'tests', 'help', 'you', 'improve', 'your', 'typing', 'skills', 'when', 'practicing', 'its', 'important', 'maintain', 'proper', 'posture', 'and', 'hand', 'positioning', 'sit', 'straight', 'keep', 'your', 'feet', 'flat', 'the', 'floor', 'and', 'position', 'your', 'hands', 'that', 'your', 'fingers', 'are', 'resting', 'the', 'home', 'row', 'keys', 'the', 'home', 'row', 'keys', 'are', 'the', 'middle', 'row', 'letters', 'the', 'keyboard', 'asdf', 'for', 'the', 'left', 'hand', 'and', 'jkl', 'for', 'the', 'right', 'hand', 'your', 'thumbs', 'should', 'rest', 'lightly', 'the', 'space', 'bar', 'you', 'type', 'try', 'keep', 'your', 'eyes', 'the', 'screen', 'rather', 'than', 'looking', 'down', 'the', 'keyboard', 'this', 'will', 'help', 'you', 'develop', 'muscle', 'memory', 'and', 'improve', 'your', 'typing', 'speed', 'may', 'feel', 'challenging', 'first', 'but', 'with', 'consistent', 'practice', 'youll', 'find', 'that', 'you', 'can', 'type', 'without', 'the', 'keys', 'addition', 'practicing', 'regularly', 'its', 'also', 'helpful', 'take', 'breaks', 'and', 'stretch', 'your', 'hands', 'and', 'fingers', 'typing', 'for', 'long', 'periods', 'time', 'can', 'lead', 'fatigue', 'and', 'discomfort', 'sure', 'give', 'your', 'hands', 'rest', 'every', 'now', 'and', 'then', 'stretching', 'exercises', 'such', 'spreading', 'your', 'fingers', 'wide', 'and', 'then', 'making', 'fist', 'can', 'help', 'relieve', 'tension', 'and', 'prevent', 'strain', 'another', 'tip', 'for', 'improving', 'your', 'typing', 'skills', 'use', 'all', 'ten', 'fingers', 'many', 'people', 'type', 'using', 'only', 'few', 'fingers', 'which', 'can', 'slow', 'them', 'down', 'and', 'lead', 'errors', 'using', 'all', 'ten', 'fingers', 'you', 'can', 'distribute', 'the', 'workload', 'more', 'evenly', 'and', 'type', 'more', 'efficiently', 'there', 'are', 'many', 'online', 'tutorials', 'and', 'guides', 'that', 'can', 'teach', 'you', 'proper', 'finger', 'placement', 'and', 'typing', 'techniques', 'you', 'continue', 'practice', 'youll', 'likely', 'notice', 'that', 'your', 'typing', 'speed', 'and', 'accuracy', 'improve', 'over', 'time', 'its', 'important', 'set', 'realistic', 'goals', 'and', 'track', 'your', 'progress', 'for', 'example', 'you', 'might', 'aim', 'increase', 'your', 'typing', 'speed', 'words', 'per', 'minute', 'each', 'week', 'keep', 'mind', 'that', 'everyone', 'progresses', 'their', 'own', 'pace', 'dont', 'get', 'discouraged', 'you', 'dont', 'see', 'immediate', 'results', 'addition', 'practicing', 'with', 'typing', 'tests', 'you', 'can', 'also', 'improve', 'your', 'skills', 'typing', 'real-world', 'content', 'for', 'example', 'you', 'might', 'try', 'typing', 'out', 'articles', 'essays', 'even', 'your', 'own', 'thoughts', 'and', 'ideas', 'this', 'will', 'help', 'you', 'get', 'used', 'typing', 'different', 'types', 'text', 'and', 'improve', 'your', 'overall', 'fluency', 'another', 'way', 'enhance', 'your', 'typing', 'skills', 'learn', 'keyboard', 'shortcuts', 'keyboard', 'shortcuts', 'are', 'combinations', 'keys', 'that', 'perform', 'specific', 'functions', 'such', 'copying', 'pasting', 'saving', 'document', 'memorizing', 'and', 'using', 'these', 'shortcuts', 'you', 'can', 'save', 'time', 'and', 'work', 'more', 'efficiently', 'some', 'common', 'keyboard', 'shortcuts', 'include', 'for', 'copy', 'for', 'paste', 'and', 's', 'for', 'save', 'its', 'also', 'important', 'stay', 'motivated', 'and', 'have', 'fun', 'while', 'practicing', 'typing', 'can', 'sometimes', 'feel', 'repetitive', 'try', 'mix', 'things', 'using', 'different', 'typing', 'games', 'and', 'challenges', 'many', 'typing', 'websites', 'offer', 'games', 'that', 'make', 'practice', 'more', 'enjoyable', 'and', 'engaging', 'for', 'example', 'you', 'might', 'try', 'game', 'where', 'you', 'have', 'type', 'words', 'they', 'fall', 'from', 'the', 'top', 'the', 'screen', 'race', 'against', 'the', 'clock', 'see', 'how', 'many', 'words', 'you', 'can', 'type', 'minute', 'conclusion', 'typing', 'valuable', 'skill', 'that', 'can', 'benefit', 'you', 'many', 'areas', 'life', 'whether', 'youre', 'typing', 'email', 'writing', 'report', 'chatting', 'with', 'friends', 'being', 'able', 'type', 'quickly', 'and', 'accurately', 'can', 'save', 'you', 'time', 'and', 'make', 'your', 'work', 'more', 'efficient', 'practicing', 'regularly', 'maintaining', 'proper', 'posture', 'and', 'using', 'all', 'ten', 'fingers', 'you', 'can', 'improve', 'your', 'typing', 'skills', 'and', 'become', 'more', 'confident', 'typist', 'remember', 'set', 'realistic', 'goals', 'track', 'your', 'progress', 'and', 'have', 'fun', 'along', 'the', 'way', 'with', 'dedication', 'and', 'persistence', 'youll', 'typing', 'like', 'pro', 'time', 'vex', 'wax', 'syzygy', 'candle', 'wax', 'elephant', 'attention', 'dog', 'ubiquitous', 'quiz', 'learning', 'moon', 'candle', 'jam', 'fuzz', 'mistake', 'bicycle', 'jump', 'egg', 'ivory', 'garden', 'violin', 'fuzz', 'kaleidoscope', 'tsunami', 'soccer', 'euphoria', 'kaleidoscope', 'ubiquitous', 'acquiesce', 'rabbit', 'car', 'butter', 'frequency', 'nest', 'quiz', 'network', 'violin', 'fjord', 'jump', 'mistake', 'random', 'fuzz', 'firefly', 'king', 'van', 'fuzz', 'gazebo', 'jungle', 'ice', 'machine', 'jacket', 'acorn', 'machine', 'euphoria', 'duck', 'dyslexia', 'jazz', 'network']


    def error_map(self):
        resq = requests.get()

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
        top_letters = set(cls.get_top_mistake_letters(5))
        print("Top mistake letters:", top_letters)
    
        short_words = [word for word in cls.word_list if len(word) <= 6]
    
        # Filter and only keep words that match at least one top letter
        filtered_words = []
        filtered_vectors = []
    
        for word in short_words:
            vec = cls.word_to_vector(word, top_letters)
            if vec.sum() > 0:
                filtered_words.append(word)
                filtered_vectors.append(vec)
    
        if not filtered_words:
            return []
    
        word_vectors = np.array(filtered_vectors)
    
        knn = NearestNeighbors(n_neighbors=min(100, len(filtered_words)), metric="cosine")
        knn.fit(word_vectors)
    
        target_vec = np.zeros(26)
        for ch in top_letters:
            target_vec[ord(ch) - ord('a')] = 1
    
        distances, indices = knn.kneighbors([target_vec])
    
        # print("Suggested Words (Length <= 6):")
        suggested_words = [filtered_words[i] for i in indices[0]]
        return suggested_words

    # @classmethod
    # def predict_words(cls):
    #     top_letters = set(cls.get_top_mistake_letters(5))
    #     word_vectors = np.array([
    #         cls.word_to_vector(word, top_letters) for word in cls.word_list
    #     ])

    #     knn = NearestNeighbors(n_neighbors=100, metric="cosine")
    #     knn.fit(word_vectors)

    #     # Synthetic vector with all top mistake letters
    #     target_vec = np.zeros(26)
    #     for ch in top_letters:
    #         target_vec[ord(ch) - ord('a')] = 1

    #     distances, indices = knn.kneighbors([target_vec])

    #     print("Suggested Words (KNN based on High Mistake Letters):")
    #     raw_suggested_words = [cls.word_list[i] for i in indices[0]]
    #     # filter_words = [i for i in raw_suggested_words if len(i) <= 5]
    #     # print("filter_words",raw_suggested_words)
    #     raw_suggested_words = [cls.word_list[i] for i in indices[0]]
    #     filtered_words = [word for word in raw_suggested_words if len(word) <= 6]
    #     return filtered_words


# Run the prediction
# Suggest.predict_words()

