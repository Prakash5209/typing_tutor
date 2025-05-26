import module1
from inputchecker import LiveInputChecker
from filter_save import Filter_and_save
import smtplib
import requests

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTreeWidgetItem
from PyQt5.QtCore import pyqtSignal, QThread, QObject, QTimer

from working.account import Register, Login, Account_recovery, Verification_code,Logout
from working.filter import Tracker

from api.ml.handler import predict_practice_word
import sys

import time


temp: str = ""



class Worker(QObject):
    finished = pyqtSignal()

    _should_stop = False
    typing_time: int = 0
    status: bool = False

    def run(self):
        print("worker started")
        # status = True
        self.change_status(b=True)
        start = time.time()
        while not self._should_stop:
            result = time.time() - start
            print("result", result)
            if result >= Worker.typing_time:
                break
            time.sleep(1)
        self.finished.emit()
        self.change_status(b=False)
        print("Worker finished")

    def stop(self):
        self._should_stop = True

    @classmethod
    def change_typing_time(cls, finish_time=0):
        cls.typing_time = finish_time

    @classmethod
    def change_status(cls, b):
        cls.status = b


class MyApp(QMainWindow):
    # login screen
    def __init__(self):
        super().__init__()

        uic.loadUi("login.ui", self)  # Load UI dynamically

        self.login_button.clicked.connect(self.goto_homeScreen)


        # self.passwordlineEdit.setEchoMode(QtWidgets.QLineEdit.Password)

        # login screen to register screen
        self.pushButton_2.clicked.connect(self.goto_registerScreen)



        # login screen to resetPasswordVerficadtionScreen
        self.forgotPassword_btn.clicked.connect(
            self.goto_resetPasswordVerificationScreen)

        QTimer.singleShot(0, self.auto_login_if_token_valid)

    def login_func(self):
        QMessageBox.information(self,"hello","button clicked")

    def auto_login_if_token_valid(self):
        if Login.is_authenticated():
            print("Token valid. Redirecting to TypingScreen.")
            widget.setCurrentIndex(widget.currentIndex() + 3)
        else:
            print("Token not found or invalid.")

        # self.showMaximized()
    def show_message(self):
        print('login button pressed')
        # QMessageBox.information(self, "Hello", "Button Clicked!")

    def goto_registerScreen(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def goto_homeScreen(self):
        username = self.usernamelineEdit.text()
        password = self.passwordlineEdit.text()

        login = Login(username, password)
        response_status = login.get_user()

        # if okay go to TypingScreen
        try:
            if response_status.status_code == 200:
                widget.setCurrentIndex(widget.currentIndex() + 3)
                print(e)
        except Exception as e:
            print("response_status.status_code", e)


    def goto_resetPasswordVerificationScreen(self):
        widget.setCurrentIndex(widget.currentIndex() + 2)


class RegisterScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("register.ui", self)

        # self.create_account.connect(self.create_account_button_function)
        self.create_account_button.clicked.connect(
            self.create_account_button_function)
        self.register_b_login.clicked.connect(self.gotoScreen1)

    def create_account_button_function(self):
        email = self.email_lineEdit.text()
        username = self.username_lineEdit_2.text()
        password = self.password_lineEdit_3.text()
        confirm_password = self.confirm_password_lineEdit_4.text()
        r = Register(email, username, password, confirm_password)
        returned_info = r._Register__register_new_account()

        if returned_info == 201:
            # goto login page
            self.gotoScreen1()

    def gotoScreen1(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)


class TypingScreen(QMainWindow):

    random_200_text = module1.typing_test_words()
    timer = [15, 30, 60]

    def __init__(self):
        self.no_chance = True
        super().__init__()
        uic.loadUi("home.ui", self)

        # timer option index
        self.timer_select_index = 0
        self.timer = TypingScreen.timer[self.timer_select_index]

        # time counter
        self.timer_counter = TypingScreen.timer[self.timer_select_index]

        self.practice_button.clicked.connect(self.gotoPractice)

        self.account_btn.clicked.connect(self.goto_account)
        self.test_type.textChanged.connect(self.textChangedfunc)
        self.test_refresh_button.clicked.connect(self.refresh_typing_text)

        # change the timer options in gui
        self.time_button.setText(
            f"time: {TypingScreen.timer[self.timer_select_index]}")
        self.time_button.clicked.connect(self.selectTime)

        self.timer_thread = None
        self.worker = None

        # dynamice text to
        self.testTextBrowser.setMarkdown(self.random_200_text)

        # sending random_200_text to this method
        self.liveinput = LiveInputChecker(
            self.random_200_text, self.testTextBrowser)



        # print("ultimate",self.liveinput.finally_return())

        # sending random_200_text to this method
        # self.filter_save = Filter_and_save(self.random_200_text)

        self.update_time = QTimer(self)
        self.update_time.timeout.connect(self.tracktimer)
        self.timer_started = False

    def selectTime(self):

        if self.timer_select_index >= len(TypingScreen.timer)-1:
            self.timer_select_index = 0
        else:
            self.timer_select_index += 1

        if not Worker.status:
            self.timer_counter = TypingScreen.timer[self.timer_select_index]
            Worker.change_typing_time(
                finish_time=TypingScreen.timer[self.timer_select_index])
            self.time_button.setText(
                f"time: {TypingScreen.timer[self.timer_select_index]}")

        # gui timer won't change until next operation

    def gotoPractice(self):
        # thread cleaning
        self.thread_cleanup()

        # stop the time tracker by assigning 0
        self.timer_counter = 0

        widget.setCurrentIndex(widget.currentIndex() + 1)

    def goto_account(self):
        # thread cleaning
        self.thread_cleanup()

        # stop the time tracker by assigning 0
        self.timer_counter = 0

        widget.setCurrentIndex(widget.currentIndex() + 2)

    def tracktimer(self):
        self.time_button.setText("time: " + str(self.timer_counter))
        self.timer_counter -= 1

        if self.timer_counter < 1:
            self.update_time.stop()
            # self.timer_counter = TypingScreen.timer[self.timer_select_index]
            self.timer_started = False

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
        # set self.no_chance = True to reset
        print("resetting the thread to ",self.no_chance)
        self.no_chance = True


        # Stop the timer explicitly
        self.update_time.stop()
        self.timer_started = False  # Reset the state

        # refresh the timer and reset the text of time_button
        self.time_button.setText(
            "time: "+str(TypingScreen.timer[self.timer_select_index]))

        # enable the linedit after refreshing the
        self.test_type.setEnabled(True)

        # resetting self.timer_counter by assigning timer_counter to 0
        self.timer_counter = TypingScreen.timer[self.timer_select_index]

        # random_200_text = module1.typing_test_words()
        self.assign_random_text()

        # self.filter_save
        # self.filter_save = Filter_and_save(self.random_200_text)

        # send to typing_test_words_from_TypingScreen
        self.liveinput = LiveInputChecker(
            self.random_200_text, self.testTextBrowser)

        self.testTextBrowser.setMarkdown(self.random_200_text)

        # clearing the input fields when refreshing the text
        self.test_type.blockSignals(True)
        self.test_type.setText("")
        self.test_type.blockSignals(False)

        # stop the worker thread when words is finished
        Worker.change_typing_time(finish_time=25)

        self.thread_cleanup()


    @classmethod
    def assign_random_text(cls):
        cls.random_200_text = module1.typing_test_words()

    def textChangedfunc(self, strg):


        # print("is_authenticated", Login.is_authenticated())
        Worker.change_typing_time(
            finish_time=TypingScreen.timer[self.timer_select_index])
        global temp
        temp = strg

        if not self.timer_started:
            self.timer_started = True
            self.update_time.start(1000)

        input_check = self.liveinput.inputcheck(strg)

        if input_check != None:  # stop the worker thread when words is finished
            Worker.change_typing_time()  # default prams: finish_time = 0

            # stoping the timer (count down)
            self.update_time.stop()
            self.timer_started = False

        # test = self.filter_save.set_input_lst(strg)

        # if self.liveinput.wordindex <= 0 and len(strg) <= 1:
        #     self.thread_timer()

        if self.no_chance:
            print("no_change")
            self.thread_timer()
            self.no_chance = False


        if strg.endswith(" "):
            temp = strg
            self.liveinput.save_previous_word(temp)
            self.liveinput.wordindex += 1
            self.test_type.setText("")

    def thread_timer(self):
        self.thread_cleanup()

        self.timer_thread = QThread()
        self.worker = Worker()

        self.worker.moveToThread(self.timer_thread)

        self.timer_thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.worker_progress)
        # self.timer_thread.wait(500)
        self.worker.finished.connect(self.timer_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.timer_thread.finished.connect(self.timer_thread.deleteLater)

        self.timer_thread.start()

    def worker_progress(self):
        print("finished and deleted")

        # sending to 
        raw_user_lst = self.liveinput.user_raw_text()
        # print("Test raw_user_lst",raw_user_lst)
        track = Tracker(TypingScreen.random_200_text,raw_user_lst)
        track.track_characters()
        res = track.create_report(self.timer)

        # print("res",res)

        for key, value in res.items():
            key_item = QTreeWidgetItem()
            key_item.setText(0, str(key))     # Column 0: name
            key_item.setText(1, str(value))   # Column 1: value
            self.treeWidget.addTopLevelItem(key_item)
        # sending random generated text to filter
        # self.send_strg = Filter_and_save(self.random_200_text)
        # self.filter_save.missedkey()
        # disable the lineedit
        self.test_type.setEnabled(False)
        self.worker = None


class PracticeScreen(QMainWindow):
    random_200_text = predict_practice_word()
    timer = [15, 30, 60]

    def __init__(self):
        self.no_chance = True
        super().__init__()
        uic.loadUi("practice.ui", self)

        # timer option index    def selectTime
        self.timer_select_index = 0
        self.timer = PracticeScreen.timer[self.timer_select_index]
        # time counter

        self.timer_counter = PracticeScreen.timer[self.timer_select_index]

        self.test_button.clicked.connect(self.gotoHome)
        self.account_btn.clicked.connect(self.goto_account)

        self.lineEdit.textChanged.connect(self.textChangedfunc)
        self.practice_refresh.clicked.connect(self.refresh_typing_text)
        # change the timer options in gui

        self.time_button.setText(
            f"time: {TypingScreen.timer[self.timer_select_index]}")
        self.time_button.clicked.connect(self.selectTime)

        self.timer_thread = None
        self.worker = None

        self.practiceTextBrowser.setMarkdown(PracticeScreen.random_200_text)

        self.liveinput = LiveInputChecker(
            PracticeScreen.random_200_text, self.practiceTextBrowser)

        self.update_time = QTimer(self)
        self.update_time.timeout.connect(self.tracktimer)
        self.timer_started = False

    def gotoHome(self):
        # thread cleaning
        self.thread_cleanup()
        widget.setCurrentIndex(widget.currentIndex() - 1)

    def goto_account(self):
        # thread cleaning
        self.thread_cleanup()
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def predict_practice_word():
        res = requests.get("http://localhost:8000/practice-words")
        # print("predict_practice_word",res.json())



    def selectTime(self):
        if self.timer_select_index >= len(TypingScreen.timer)-1:

            self.timer_select_index = 0
        else:
            self.timer_select_index += 1

        if not Worker.status:
            self.timer_counter = TypingScreen.timer[self.timer_select_index]
            Worker.change_typing_time(
                finish_time=TypingScreen.timer[self.timer_select_index])
            self.time_button.setText(
                f"time: {TypingScreen.timer[self.timer_select_index]}")

    def tracktimer(self):
        self.time_button.setText("time: " + str(self.timer_counter))
        self.timer_counter -= 1

        if self.timer_counter < 1:
            self.update_time.stop()
            # self.timer_counter = TypingScreen.timer[self.timer_select_index]
            self.timer_started = False

    def refresh_typing_text(self):
        # print("resetting the thread to ",self.no_chance)
        self.no_chance = True

        # Stop the timer explicitly
        self.update_time.stop()

        self.timer_started = False  # Reset the state
        # refresh the timer and reset the text of time_button
        self.time_button.setText(
            "time: "+str(TypingScreen.timer[self.timer_select_index]))

        # enable the linedit after refreshing the
        self.lineEdit.setEnabled(True)

        # resetting self.timer_counter by assigning timer_counter to 0
        self.timer_counter = TypingScreen.timer[self.timer_select_index]

        # self.random_200_text = module1.typing_test_words()
        self.assign_random_text()

        # self.filter_save
        # self.filter_save = Filter_and_save(self.random_200_text)

        # send to typing_test_words_from_TypingScreen
        self.liveinput = LiveInputChecker(
            PracticeScreen.random_200_text, self.practiceTextBrowser)

        self.practiceTextBrowser.setMarkdown(PracticeScreen.random_200_text)

        # clearing the input fields when refreshing the text
        self.lineEdit.blockSignals(True)
        self.lineEdit.setText("")
        self.lineEdit.blockSignals(False)

        # stop the worker thread when words is finished
        Worker.change_typing_time(finish_time=25)

        self.thread_cleanup()

    @classmethod
    def assign_random_text(cls):
        cls.random_200_text = predict_practice_word()



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

                        # resetting self.timer_counter by assigning timer_counter to 0
                        self.timer_counter = TypingScreen.timer[self.timer_select_index]

                        self.timer_thread.wait()
            except RuntimeError:
                pass  # Already deleted
            finally:
                self.timer_thread = None
                self.worker = None

    def textChangedfunc(self, strg):

        Worker.change_typing_time(
            finish_time=PracticeScreen.timer[self.timer_select_index])
        global temp
        temp = strg

        if not self.timer_started:
            self.timer_started = True
            self.update_time.start(1000)

        input_check = self.liveinput.inputcheck(strg)

        if input_check != None:  # stop the worker thread when words is finished
            Worker.change_typing_time()  # default prams: finish_time = 0

            # stoping the timer (count down)
            self.update_time.stop()
            self.timer_started = False

            # sending raw user input to Filter_and_save
        # test = self.filter_save.set_input_lst(strg)

        if self.no_chance:
            print("no_change")
            self.thread_timer()
            self.no_chance = False


        if strg.endswith(" "):
            temp = strg
            self.liveinput.save_previous_word(temp)
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
        self.worker.finished.connect(self.worker.deleteLater)
        self.timer_thread.finished.connect(self.timer_thread.deleteLater)

        self.timer_thread.start()

    def worker_progress(self):

        print("finished and deleted")

        # sending to 
        raw_user_lst = self.liveinput.user_raw_text()
        # print("Test raw_user_lst",raw_user_lst)
        track = Tracker(PracticeScreen.random_200_text,raw_user_lst)
        track.track_characters()
        track.create_report(self.timer)


        # disable the lineedit
        self.lineEdit.setEnabled(False)
        self.worker = None


class ResetPasswordVerificationScreen(QMainWindow):
    def __init__(self):
        self.obj = None
        super().__init__()
        uic.loadUi("forgotPasswordVerificationCode.ui", self)

        # back to login screen from resetPasswordVerficadtionScreen
        self.forgotPasswordCancel_btn.clicked.connect(self.backToLoginScreen)
        self.send_code_to_email_pushButton_2.clicked.connect(
            self.send_code_to_email)
        self.recovery_code_submit.clicked.connect(
            self.confirm_recovery_code_func)

    def backToLoginScreen(self):  # from resetPasswordVerficadtionScreen

        widget.setCurrentIndex(widget.currentIndex() - 2)

    def send_code_to_email(self):
        username = self.username_lineEdit.text()
        self.obj = Account_recovery(username)
        self.obj.send_mail()

    def confirm_recovery_code_func(self):
        code = self.code_lineEdit.text()
        obj = Verification_code()
        ret = obj.confirm_recovery_code(code)
        if ret:
            reset_password_screen = widget.widget(widget.currentIndex() + 4)
            reset_password_screen.setverification_obj(ret)
            widget.setCurrentIndex(widget.currentIndex() + 4)
        else:
            return f"return {ret}"


class ResetPassword(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("password_reset.ui", self)
        self.submit.clicked.connect(self.submit_new_password)

    def setverification_obj(self, obj):
        self.verification_obj = obj
        self.email_label.setText(self.verification_obj)

    def submit_new_password(self):
        new_pass = self.newpasswordLineEdit.text()
        confirm_pass = self.confirmpasswordLineEdit.text()
        obj = Verification_code()
        obj.create_new_password(self.verification_obj, new_pass, confirm_pass)


    # class AccountScreen(QMainWindow):
    #     def __init__(self):
    #         super().__init__()
    #         uic.loadUi("account.ui", self)
    # 
    #         # back to login screen from resetPasswordVerficadtionScreen
    #         self.logout_btn.clicked.connect(self.backToLoginScreen)
    # 
    #     def load_data(self):
    #         ...
    # 
    #     def backToLoginScreen(self):  # from resetPasswordVerficadtionScreen
    #         logout = Logout()
    #         logout.remove_token()
    #         widget.setCurrentIndex(widget.currentIndex() - 5)
    

class AccountScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("account.ui", self)  # Load your UI file here

        # Connect logout button (if needed)
        self.logout_btn.clicked.connect(self.backToLoginScreen)

        # back to typing screen
        self.test_session.clicked.connect(lambda: widget.setCurrentIndex(widget.currentIndex() - 2))

        # back to practice screen
        self.practice_button.clicked.connect(lambda: widget.setCurrentIndex(widget.currentIndex() - 1))

        self.load_reports()
        # Load reports on startup

    def load_reports(self):
        tk = Login.is_authenticated()
        headers = {
            "Authorization": f"Bearer {tk}",
            "Content-Type": "application/json"
        }
        # Example payload, replace 'rwpm', 'wpm', 'accu' with actual values or remove if not needed
        js = {
            "wpm": 70,    # example value
            "rwpm": 65,   # example value
            "accuracy": 90 # example value
        }

        try:
            response = requests.get("http://localhost:8000/get-report", headers=headers)
            response.raise_for_status()
            data = response.json()
            # print("response",data)

            # Assuming data is a list of report dicts; adjust if API returns differently
            self.populate_tree(data)

        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to load reports:\n{str(e)}")

    def populate_tree(self, reports):
        self.treeWidget.clear()
    
        self.treeWidget.setColumnCount(8)
        self.treeWidget.setHeaderLabels([
            "SN", "Session ID", "User ID", "WPM", "Accuracy", "RWPM", "Created At", "File Path"
        ])
    
        for i, report in enumerate(reports, start=1):
            item = QTreeWidgetItem([
                str(i),
                report.get("session_id", ""),
                str(report.get("user_id", "")),
                str(report.get("wpm", "")),
                str(report.get("accuracy", "")),
                str(report.get("rwpm", "")),
                report.get("create_at", ""),
                report.get("file_path", ""),
            ])
            self.treeWidget.addTopLevelItem(item)

    def backToLoginScreen(self):
        logout = Logout()
        logout.remove_token()
        widget.setCurrentIndex(widget.currentIndex() - 5)

# Run the application
app = QApplication([])


# styling

with open("style/style.qss") as f:
    app.setStyleSheet(f.read())


widget = QtWidgets.QStackedWidget()  # testing

login = MyApp()
resetConfirmation = ResetPasswordVerificationScreen()
register = RegisterScreen()
typingScreen = TypingScreen()
practicescreen = PracticeScreen()
accountscreen = AccountScreen()
resetpassword = ResetPassword()

widget.addWidget(login)
widget.addWidget(register)
widget.addWidget(resetConfirmation)
widget.addWidget(typingScreen)
widget.addWidget(practicescreen)
widget.addWidget(accountscreen)
widget.addWidget(resetpassword)

widget.show()
app.exec_()
