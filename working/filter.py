import string

class Tracker:
    def __init__(self, text, raw_char):
        self.text = text.lower().split()
        self.raw_char = raw_char

    def track_characters(self, target_char=None):
        typed = list(self.raw_char)

        self.missed_char = {key: 0 for key in string.ascii_lowercase}
        self.typed_char = {key: 0 for key in string.ascii_lowercase}

        lst_text = list(map(lambda x:list(x),self.text))

        for i in range(len(self.raw_char)):
            if len(self.raw_char[i]) == len(lst_text[i]):
                for j in range(len(self.raw_char[i])):
                    if self.raw_char[i][j] != lst_text[i][j]:
                        self.missed_char[lst_text[i][j]] += 1
                        self.typed_char[self.raw_char[i][j]] += 1


            elif len(self.raw_char[i]) < len(lst_text[i]):
                for j in range(len(self.raw_char[i])):
                    if self.raw_char[i][j] != lst_text[i][j]:
                        self.missed_char[lst_text[i][j]] += 1
                        self.typed_char[self.raw_char[i][j]] += 1
                for k in range(1,(len(lst_text[i])-len(self.raw_char[i]))+1):
                    self.missed_char[lst_text[i][-k]] += 1


            elif len(self.raw_char[i]) > len(lst_text[i]):
                for j in range(len(lst_text[i])):
                    if self.raw_char[i][j] != lst_text[i][j]:
                        self.missed_char[lst_text[i][j]] += 1
                        self.typed_char[self.raw_char[i][j]] += 1
                for k in range(1,(len(self.raw_char[i])-len(lst_text[i]))+1):
                    self.typed_char[self.raw_char[i][-k]] += 1


        print(self.missed_char)
        print(self.typed_char)
