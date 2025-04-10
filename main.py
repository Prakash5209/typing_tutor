import module1
from inputchecker import LiveInputChecker

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow,QTextBrowser
from PyQt5.QtCore import Qt


class MyApp(QMainWindow):
    #login screen
    def __init__(self):
        super().__init__()
        uic.loadUi("login.ui", self)  # Load UI dynamically

        self.pushButton.clicked.connect(self.goto_homeScreen) #login screen to TypingScreen

        self.pushButton_2.clicked.connect(self.goto_registerScreen) # login screen to register screen

        self.forgotPassword_btn.clicked.connect(self.goto_resetPasswordVerificationScreen) # login screen to resetPasswordVerficadtionScreen

        self.showMaximized()

    def show_message(self):
        print('login button pressed')
        # QMessageBox.information(self, "Hello", "Button Clicked!")

    def goto_registerScreen(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def goto_homeScreen(self):
        widget.setCurrentIndex(widget.currentIndex() + 3)

    def goto_resetPasswordVerificationScreen(self):
        widget.setCurrentIndex(widget.currentIndex() + 2)



class RegisterScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("register.ui",self)

        self.pushButton.clicked.connect(self.show_message)
        self.register_b_login.clicked.connect(self.gotoScreen1)

    def show_message(self):
        print("some button")

    def gotoScreen1(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)


class TypingScreen(QMainWindow):

    random_200_text = module1.typing_test_words()

    def __init__(self):
        super().__init__()
        uic.loadUi("home.ui",self)

        self.practice_button.clicked.connect(self.gotoPractice)

        self.account_btn.clicked.connect(self.goto_account)
        self.test_type.textChanged.connect(self.textChangedfunc)
        self.test_refresh_button.clicked.connect(self.refresh_typing_text)

        # dynamice text to
        self.testTextBrowser.setMarkdown(self.random_200_text)
        # self.testTextBrowser.setMarkdown(f"<span style='color:red;'>{self.random_200_text}</span>")

        # sending random_200_text to this method 
        self.liveinput = LiveInputChecker(self.random_200_text,self.testTextBrowser)

    def gotoPractice(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def goto_account(self):
        widget.setCurrentIndex(widget.currentIndex() + 2)

    def refresh_typing_text(self):
        self.random_200_text = module1.typing_test_words()
        # send to typing_test_words_from_TypingScreen
        self.liveinput = LiveInputChecker(self.random_200_text,self.testTextBrowser)

        self.testTextBrowser.setMarkdown(self.random_200_text)

        # clearing the input fields when refreshing the text
        self.test_type.setText("")

    def textChangedfunc(self,strg):
        ok = self.liveinput.inputcheck(strg)
        # p = self.liveinput.font_color(key_info)
        # print("p",p)

        if strg.endswith(" "):
            self.liveinput.wordindex += 1
            self.test_type.setText("")



class PracticeScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("practice.ui",self)

        self.test_button.clicked.connect(self.gotoHome)
        self.account_btn.clicked.connect(self.goto_account)

    def gotoHome(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)

    def goto_account(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)



class ResetPasswordVerificationScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("forgotPasswordVerificationCode.ui",self)

        self.forgotPasswordCancel_btn.clicked.connect(self.backToLoginScreen) # back to login screen from resetPasswordVerficadtionScreen

    def backToLoginScreen(self): # from resetPasswordVerficadtionScreen
        widget.setCurrentIndex(widget.currentIndex() - 2)


class AccountScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("account.ui",self)

        self.logout_btn.clicked.connect(self.backToLoginScreen) # back to login screen from resetPasswordVerficadtionScreen

    def backToLoginScreen(self): # from resetPasswordVerficadtionScreen
        widget.setCurrentIndex(widget.currentIndex() - 5)


# Run the application
app = QApplication([])


widget = QtWidgets.QStackedWidget()  # testin

login = MyApp()
resetConfirmation = ResetPasswordVerificationScreen()
register = RegisterScreen()
typingScreen = TypingScreen()
practicescreen = PracticeScreen()
accountscreen = AccountScreen()

widget.addWidget(login)
widget.addWidget(register)
widget.addWidget(resetConfirmation)
widget.addWidget(typingScreen)
widget.addWidget(practicescreen)
widget.addWidget(accountscreen)

widget.show()
app.exec_()
