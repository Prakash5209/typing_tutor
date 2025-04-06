from typing import Dict,List

# TypingScreen from main.py
class LiveInputChecker:
    def __init__(self,text,text_browser):
        self.wordindex = 0 
        self.text = text
        self.text_browser = text_browser
        self.typed_word_lst = []
        self.typed_raw_word_lst = []

        self.raw_letter_lst = []
        self.track_raw_letter_lst = []

    def __str__(self):
        return self.text

    def inputcheck(self,word):
        text_lst = self.text.split()
        text_nested_lst = list(map(lambda x:list(x),text_lst))

        if len(text_nested_lst) - 1 >= self.wordindex:
            text_in_word_lst = text_nested_lst[self.wordindex]
        else:
            text_in_word_lst = text_nested_lst[len(text_nested_lst)-1]


        word_lst = list(word)


        if len(word_lst) > 0 and word_lst[-1] == " ":
            word_lst.remove(" ")
       
        # add mistake letter after word completion
        raw_letter_status = [y for _,y in zip(text_in_word_lst,word_lst)]
        raw_letter_status.extend(word_lst[len(text_in_word_lst):])
        
        word_status = {}
        word_status['wordindex'] = self.wordindex
        word_status['raw_letter_status'] = raw_letter_status
        self.letter_color_confirmed(word_status,text_nested_lst)

        # print("okay",okay)
        # self.typed_word_lst.append(okay)

        # print("typed_word_lst",self.typed_word_lst)

        # changing current cursor background color
        try:
            print("future".center(45,"-"),text_nested_lst[self.wordindex][len(word_lst)])

            front = list(map(lambda x:"".join(x),text_nested_lst[:self.wordindex]))
            front_middle = ["".join(text_nested_lst[self.wordindex][:len(word_lst)])]

            open_span = ['<span style="background:skyblue">']
            middle = [text_nested_lst[self.wordindex][len(word_lst)]]
            close_span = ['</span>']

            back_middle = ["".join(text_nested_lst[self.wordindex][len(word_lst) + 1:])]
            back = list(map(lambda x:"".join(x),text_nested_lst[self.wordindex + 1:]))

            color = " ".join(front + front_middle + open_span + middle + close_span + back_middle + back)
            self.text_browser.setHtml(color)

            #self.text_browser.setHtml(("".join(text_nested_lst[self.wordindex][:len(word_lst)]) + '<span style="background:skyblue">' + text_nested_lst[self.wordindex][len(word_lst)] + '</span>' + "".join(text_nested_lst[self.wordindex][len(word_lst) + 1:])))
        except:
            print("hit space bar".center(90,'-')) 


    def letter_color_confirmed(self, word_status_dict: Dict, context_text: List) -> None:
        letter_status = word_status_dict.get("raw_letter_status", [])
        word_index = word_status_dict.get("wordindex", 0)
        current_word = context_text[word_index] if word_index < len(context_text) else []

        # Reset if no letters (new word)
        if not letter_status:
            self.track_raw_letter_lst = []
            self.raw_letter_lst = []
            return

        # Handle backspace/edit in middle of word
        if len(letter_status) != len(self.track_raw_letter_lst):
            # Rebuild both lists completely to handle any position deletion
            self.track_raw_letter_lst = []
            self.raw_letter_lst = []
            
            for i, char in enumerate(letter_status):
                # Check if letter is correct (within bounds and matches)
                is_correct = i < len(current_word) and char == current_word[i]
                color = '<span style="color:green">' + char + '</span>' if is_correct else '<span style="color:red">' + char + '</span>'
                self.raw_letter_lst.append(color)
                self.track_raw_letter_lst.append(char)
        else:
            # Only process new letters (normal typing)
            if len(letter_status) > len(self.track_raw_letter_lst):
                new_char = letter_status[-1]
                is_correct = (len(letter_status) <= len(current_word) and (new_char == current_word[len(letter_status)-1]))
                color = '<span style="color:green">' + new_char + '</span>' if is_correct else '<span style="color:red">' + new_char + '</span>'
                self.raw_letter_lst.append(color)
                self.track_raw_letter_lst.append(new_char)


        # Update word list (only one entry per word)
        if len(self.typed_word_lst) <= word_index:
            self.typed_word_lst.append(self.track_raw_letter_lst.copy())
        else:
            self.typed_word_lst[word_index] = self.track_raw_letter_lst.copy()


        print("raw_letter_lst", self.raw_letter_lst)



        if len(self.typed_raw_word_lst) == word_index:
            self.typed_raw_word_lst.append(['mouse'])
            self.typed_raw_word_lst[word_index] = self.raw_letter_lst.copy()
        elif len(self.typed_raw_word_lst) != word_index:
            self.typed_raw_word_lst[word_index] = self.raw_letter_lst.copy()

