import numpy as np

# random 200 words generator


# def typing_test_words():
#     with open("words_alpha.txt", "r") as word:
#         re = word.read()
#         lst = re.split()
#         npary = np.array([i for i in lst if len(i) <= 6])
#         random_words = np.random.choice(npary,size=30)
#         print(random_words)
#         return " ".join(random_words)


def typing_test_words():
    with open("TestTypingWords","r") as word:
        rawlst = [i.split() for i in word]
        flatten_array = np.concatenate(rawlst)
        cleaned_array = np.array(
            list(map(lambda x: x.replace('.', '').replace(',', ''), flatten_array)))
        random_words = np.random.choice(cleaned_array, size=30)
        return " ".join(random_words)
