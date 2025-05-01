from custom_algo import get_best_matches_from_file

class Filter_and_save:
    user_input_lst = []
    def __init__(self,random_text):
        self.ran_text = random_text.split()


    def __str__(self):
        return f"test {self.ran_text}"

    def set_input_lst(self,user_input):
        if user_input.endswith(" "):
            print(len(user_input.replace(" ","")))
            self.user_input_lst.append(user_input.replace(" ",""))
        return self.user_input_lst

    def missedkey(self):
        missed = []
        i = 0
        while i < len(self.user_input_lst):
            for j in range(len(self.user_input_lst[i])):
                try:
                    if self.user_input_lst[i][j] != self.ran_text[i][j]:
                        missed.append(self.ran_text[i][j])
                except Exception as e:
                    print(e)
            i += 1


        # calling the custom_algo file or word suggestion
        test = get_best_matches_from_file(missed,"large_word_list.txt","output.txt")
        print(test)
        print(missed)
        return missed
