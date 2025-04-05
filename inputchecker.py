from typing import Dict,List
# import itertools

# TypingScreen from main.py
class LiveInputChecker:
    def __init__(self,text,text_browser):
        self.wordindex = 0 
        self.text = text
        self.text_browser = text_browser
        self.typed_word_lst = []
        self.letter_lst = []
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


        print('input check',word);

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

        # changing current cursor background color
        try:
            print("future",text_nested_lst[self.wordindex][len(word_lst)])

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
            print("hit space bar") 


    def letter_color_confirmed(self,word_status_dict: Dict,context_text:List) -> int:
        green_color = lambda x: ['<span style="color:green">' + x + '</span>']
        red_color = lambda x: ['<span style="color:red">' + x + '</span>']

        letter_status = word_status_dict.get("raw_letter_status")
        word_index = word_status_dict.get("wordindex")


        if not letter_status or all(ch == " " for ch in letter_status):
            return  # Do nothing on space-only input


        # get the length of typed letters - 1
        typed_letter_index = len(word_status_dict.get('raw_letter_status')) - 1
        # len(word_status_dict.get('letter_status')[typed_letter_index]) > len(context_text[word_status_dict.get('wordindex')][typed_letter_index])

        
        if len(letter_status) <= len(self.raw_letter_lst):
            ...
        elif typed_letter_index < len(context_text[word_index]) and (context_text[word_index][typed_letter_index] == letter_status[typed_letter_index]) or (typed_letter_index + 1 > len(context_text[word_index])):
            # If the typed letter matches the expected letter
            self.raw_letter_lst.append(green_color(letter_status[typed_letter_index]))
            self.track_raw_letter_lst.append(letter_status[typed_letter_index])
        
        elif (context_text[word_index][typed_letter_index] != letter_status[typed_letter_index]) or (typed_letter_index + 1 > len(context_text[word_index])):
            # If the typed letter does not match the expected letter (red color)
            self.raw_letter_lst.append(red_color(letter_status[typed_letter_index]))
            self.track_raw_letter_lst.append(letter_status[typed_letter_index])
        else:
            ...

        # self.typed_word_lst.append(self.raw_letter_lst)

        while letter_status != self.track_raw_letter_lst:
            for i in range(len(letter_status)):
                if letter_status[i] != self.track_raw_letter_lst[i]:
                    del self.track_raw_letter_lst[i]
                    del self.raw_letter_lst[i]
            if len(letter_status) < len(self.track_raw_letter_lst):
                self.track_raw_letter_lst.pop()
                self.raw_letter_lst.pop()
            else:
                print("no pop in any list")
            print('in while loop')
            break


