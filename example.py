class Person:
    timer = 23

    def __init__(self):
        self.timer = 123

    def __str__(self):
        return str(self.timer)


clast Window:
    def change_value(self):
        print(Person.timer)


s = Window()
s.change_value()
