from sys import thread_info

from numpy import e
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
            if result >= 5:
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

        self.thread = None
        self.worker = None
        
        # dynamice text to
        self.testTextBrowser.setMarkdown(self.random_200_text)

        # sending random_200_text to this method 
        self.liveinput = LiveInputChecker(self.random_200_text,self.testTextBrowser)


    def gotoPractice(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def goto_account(self):
        widget.setCurrentIndex(widget.currentIndex() + 2)


    # def thread_cleanup(self):
    #     if hasattr(self, 'thread') and self.thread is not None:
    #         try:
    #             if self.thread.isRunning():
    #                 if hasattr(self, 'worker') and self.worker is not None:
    #                     self.worker.stop()
    #                     self.worker.finished.disconnect()
    #                     self.worker.deleteLater()
    #                 self.thread.quit()
    #                 self.thread.wait(500)
    #                 if self.thread.isRunning():
    #                     self.thread.terminate()
    #                     self.thread.wait()

    #             self.thread.deleteLater()
    #         except RuntimeError:
    #             pass
    #         finally:
    #             self.thread = None
    #             self.worker = None


    def thread_cleanup(self):
        # Disconnect all signals first
        if hasattr(self, 'worker') and self.worker is not None:
            try:
                self.worker.stop()
                self.worker.finished.disconnect()
            except RuntimeError:
                pass  # Already deleted
            
        if hasattr(self, 'thread') and self.thread is not None:
            try:
                if self.thread.isRunning():
                    self.thread.quit()
                    if not self.thread.wait(1000):
                        self.thread.terminate()
                        self.thread.wait()
            except RuntimeError:
                pass  # Already deleted
            finally:
                self.thread = None
                self.worker = None

    def refresh_typing_text(self):
        self.random_200_text = module1.typing_test_words()

        # send to typing_test_words_from_TypingScreen
        self.liveinput = LiveInputChecker(self.random_200_text,self.testTextBrowser)

        self.testTextBrowser.setMarkdown(self.random_200_text)

        # clearing the input fields when refreshing the text
        self.test_type.setText("")

        self.thread_cleanup()
        print("inspect",self.thread)
        print("inspect",self.worker)



    def textChangedfunc(self, strg):
        ok = self.liveinput.inputcheck(strg)

        if self.liveinput.wordindex <= 0 and len(strg) <= 1:
            # Thread-safe check
            # thread_alive = False
            # if hasattr(self, 'thread') and self.thread is not None:
            #     try:
            #         thread_alive = self.thread.isRunning()
            #     except RuntimeError:
            #         thread_alive = False
            # 
            # if not thread_alive:
            #     self.thread_timer()
            self.thread_timer()

        if strg.endswith(" "):
            self.liveinput.wordindex += 1
            self.test_type.setText("")

    def thread_timer(self):
        self.thread_cleanup()

        self.thread = QThread()
        self.worker = Worker()

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.worker_progress)
        self.worker.finished.connect(self.thread.quit)
        # self.thread.wait(500)
        print(self.thread.isRunning())
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()


    def worker_progress(self):
        print("finished and deleted")
        self.worker = None


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
