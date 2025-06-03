import requests
from typing import Dict, List
from working.account import Login


class LiveInputChecker:
    def __init__(self, text, text_browser):
        self.count = 0
        self.wordindex = 0
        self.text = text
        self.text_browser = text_browser
        self.typed_word_lst = []

        self.raw_letter_lst = []  # Front corrected words
        self.test_lst = []
        self.raw_char = []


    def __str__(self):
        return self.text

    def inputcheck(self, word):

        text_lst = self.text.split()
        text_nested_lst = list(map(lambda x: list(x), text_lst))

        if len(text_nested_lst) - 1 >= self.wordindex:
            text_in_word_lst = text_nested_lst[self.wordindex]
        else:
            text_in_word_lst = text_nested_lst[-1]

        word_lst = list(word)
        if len(word_lst) > 0 and word_lst[-1] == " ":
            word_lst.remove(" ")

        raw_letter_status = [y for _, y in zip(text_in_word_lst, word_lst)]
        raw_letter_status.extend(word_lst[len(text_in_word_lst):])

        word_status = {
            'wordindex': self.wordindex,
            'raw_letter_status': raw_letter_status
        }

        self.letter_color_confirmed(word_status, text_nested_lst)

        try:
            front = self.raw_letter_lst  # <<< Use raw_letter_lst directly
            middle_word = "".join(text_nested_lst[self.wordindex])
            third = list(map(lambda x: "".join(
                x), text_nested_lst[self.wordindex + 1:]))

            if word_lst != text_nested_lst[self.wordindex][:len(word_lst)]:
                open_span = ['<span style="background:red">']
            else:
                open_span = ['<span style="background:skyblue">']

            close_span = ['</span>']
            mid = ["".join(open_span + [middle_word] + close_span)]

            self.text_browser.setHtml(" " .join(front + mid + third))

        except Exception as e:
            finish_type_word = list(
                map(lambda x: "".join(x), self.raw_letter_lst))
            self.text_browser.setHtml(" ".join(finish_type_word))
            return ("exception output", e)

    def save_previous_word(self, prev_word):
        self.typed_word_lst.append(prev_word.replace(" ", ""))

    def letter_color_confirmed(self, word_status_dict: Dict, context_text: List) -> None:
        word_index = word_status_dict.get('wordindex', 0)
        raw_letter_status = word_status_dict.get('raw_letter_status', [])

        # current_word = context_text[word_index]

        def red(x):
            return f"<span style='color:red; display:inline-block; margin:0; padding:0;'>{x}</span>"

        def green(x):
            return f"<span style='color:green; display:inline-block; margin:0; padding:0;'>{x}</span>"

        if len(self.typed_word_lst) > self.count:
            self.count += 1

            typed_word = self.typed_word_lst[word_index - 1]
            context_word = context_text[self.wordindex - 1]

            if len(typed_word) > len(context_word):
                self.raw_letter_lst.append(red("".join(context_word)))
                self.raw_char.append(list(typed_word))
            else:
                if list(typed_word) == context_word:
                    self.raw_letter_lst.append(green("".join(context_word)))
                    self.raw_char.append(list(typed_word))
                else:
                    self.raw_char.append(list(typed_word))
                    self.raw_letter_lst.append(red("".join(context_word)))

            # self.user_raw_text()

    def user_raw_text(self):
        return list(map(lambda x:"".join(x),self.raw_char))
        # return self.raw_char






class Fingers:
    def __init__(self, text):
        self.text = text
        self.index = 0

    def userinput(self, current_input):
        lst_text = [i for i in self.text.split()]
        filter_current_input = current_input.replace(" ","")

        if current_input.endswith(" "):
            self.index += 1

        try:
            future = lst_text[self.index][len(filter_current_input)]
            print("future",future)
            return future
        except IndexError:
            print("hit space")
            return "space"

