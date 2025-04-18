import module1
from inputchecker import LiveInputChecker

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow,QTextBrowser
from PyQt5.QtCore import Qt, pyqtSignal,QThread,QObject

import time

class Worker(QObject):
    finished = pyqtSignal()
    _should_stop = False

    def run(self):
        print("started")
        start = time.time()
        while not self._should_stop:
            result = time.time() - start
            if result >= 30:
                break
            time.sleep(0.1)  # Add small sleep to prevent tight loop
        self.finished.emit()
        print("Worker finished")  # Debug print

    def stop(self):
        self._should_stop = True

class MyApp(QMainWindow):
    #login screen
    def __init__(self):
        super().__init__()
        uic.loadUi("login.ui", self)  # Load UI dynamically

        self.pushButton.clicked.connect(self.goto_homeScreen) #login screen to TypingScreen

        self.pushButton_2.clicked.connect(self.goto_registerScreen) # login screen to register screen

        self.forgotPassword_btn.clicked.connect(self.goto_resetPasswordVerificationScreen) # login screen to resetPasswordVerficadtionScreen

        # self.showMaximized()
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

        self.timer_thread = None
        self.worker = None
        
        # dynamice text to
        self.testTextBrowser.setMarkdown(self.random_200_text)

        # sending random_200_text to this method 
        self.liveinput = LiveInputChecker(self.random_200_text,self.testTextBrowser)


    def gotoPractice(self):
        # thread cleaning
        self.thread_cleanup()
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def goto_account(self):
        widget.setCurrentIndex(widget.currentIndex() + 2)

    def thread_cleanup(self):
        # Disconnect all signals first
        if hasattr(self, 'worker') and self.worker is not None:
            try:
                self.worker.stop()
                self.worker.finished.disconnect()
            except RuntimeError:
                pass  # Already deleted
            
        if hasattr(self, 'timer_thread') and self.timer_thread is not None:
            try:
                if self.timer_thread.isRunning():
                    self.timer_thread.quit()
                    if not self.timer_thread.wait(1000):
                        self.timer_thread.terminate()
                        self.timer_thread.wait()
            except RuntimeError:
                pass  # Already deleted
            finally:
                self.timer_thread = None
                self.worker = None

    def refresh_typing_text(self):
        # enable the linedit after refreshing the 
        self.test_type.setEnabled(True)

        self.random_200_text = module1.typing_test_words()

        # send to typing_test_words_from_TypingScreen
        self.liveinput = LiveInputChecker(self.random_200_text,self.testTextBrowser)

        self.testTextBrowser.setMarkdown(self.random_200_text)

        # clearing the input fields when refreshing the text
        self.test_type.setText("")

        self.thread_cleanup()
        print("inspect",self.timer_thread)
        print("inspect",self.worker)



    def textChangedfunc(self, strg):
        ok = self.liveinput.inputcheck(strg)

        if self.liveinput.wordindex <= 0 and len(strg) <= 1:
            self.thread_timer()

        if strg.endswith(" "):
            self.liveinput.wordindex += 1
            self.test_type.setText("")

    def thread_timer(self):
        self.thread_cleanup()

        self.timer_thread = QThread()
        self.worker = Worker()

        self.worker.moveToThread(self.timer_thread)

        self.timer_thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.worker_progress)
        self.worker.finished.connect(self.timer_thread.quit)
        # self.timer_thread.wait(500)
        print(self.timer_thread.isRunning())
        self.worker.finished.connect(self.worker.deleteLater)
        self.timer_thread.finished.connect(self.timer_thread.deleteLater)

        self.timer_thread.start()


    def worker_progress(self):
        print("finished and deleted")

        # disable the lineedit 
        self.test_type.setEnabled(False)
        self.worker = None


class PracticeScreen(QMainWindow):
    random_200_text = module1.typing_test_words()
    def __init__(self):
        super().__init__()
        uic.loadUi("practice.ui",self)

        self.test_button.clicked.connect(self.gotoHome)
        self.account_btn.clicked.connect(self.goto_account)

        self.lineEdit.textChanged.connect(self.textChangedfunc)
        self.textBrowser.setMarkdown(self.random_200_text)

        self.liveinput = LiveInputChecker(self.random_200_text,self.textBrowser)

    def gotoHome(self):
        # thread cleaning
        self.thread_cleanup()
        widget.setCurrentIndex(widget.currentIndex() - 1)

    def goto_account(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)


    def thread_cleanup(self):
        # Disconnect all signals first
        if hasattr(self, 'worker') and self.worker is not None:
            try:
                self.worker.stop()
                self.worker.finished.disconnect()
            except RuntimeError:
                pass  # Already deleted


        if hasattr(self, 'timer_thread') and self.timer_thread is not None:
            try:
                if self.timer_thread.isRunning():
                    self.timer_thread.quit()
                    if not self.timer_thread.wait(1000):
                        self.timer_thread.terminate()
                        self.timer_thread.wait()
            except RuntimeError:
                pass  # Already deleted
            finally:
                self.timer_thread = None
                self.worker = None


    def textChangedfunc(self, strg):
        ok = self.liveinput.inputcheck(strg)

        if self.liveinput.wordindex <= 0 and len(strg) <= 1:
            self.thread_timer()

        if strg.endswith(" "):
            self.liveinput.wordindex += 1
            self.lineEdit.setText("")

    def thread_timer(self):
        self.thread_cleanup()

        self.timer_thread = QThread()
        self.worker = Worker()

        self.worker.moveToThread(self.timer_thread)

        self.timer_thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.worker_progress)
        self.worker.finished.connect(self.timer_thread.quit)
        # self.timer_thread.wait(500)
        print(self.timer_thread.isRunning())
        self.worker.finished.connect(self.worker.deleteLater)
        self.timer_thread.finished.connect(self.timer_thread.deleteLater)

        self.timer_thread.start()
    def worker_progress(self):

        print("finished and deleted")

        # disable the lineedit 
        self.lineEdit.setEnabled(False)
        self.worker = None


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
