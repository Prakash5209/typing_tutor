import module1
import pyqtgraph as pg
from inputchecker import LiveInputChecker
# from filter_save import Filter_and_save
import smtplib
import requests
import datetime

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTreeWidgetItem,QTableWidgetItem
from PyQt5.QtCore import pyqtSignal, QThread, QObject, QTimer

from working.account import Register, Login, Account_recovery, Verification_code,Logout,UserInfo
from working.filter import Tracker
import numpy as np

from algo_handler import Handler_algo


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


        self.passwordlineEdit.setEchoMode(QtWidgets.QLineEdit.Password)

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
        try:
            if response_status.status_code == 200:
                # Move to TypingScreen
                widget.setCurrentIndex(widget.currentIndex() + 3)
        except Exception as e:
            print("Login failed:", e)

    def goto_resetPasswordVerificationScreen(self):
        widget.setCurrentIndex(widget.currentIndex() + 2)


class RegisterScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("register.ui", self)


        self.password_lineEdit_3.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_password_lineEdit_4.setEchoMode(QtWidgets.QLineEdit.Password)
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

        self.tutor_btn.clicked.connect(lambda: widget.setCurrentIndex(widget.currentIndex() + 4))


        # self.tutor

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

    def showEvent(self,event):
        print("typingscreen")
        if UserInfo.get_userinfo():
            self.account_btn.setText(UserInfo.get_userinfo().get("username"))
        super().showEvent(event)


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

        self.treeWidget.clear()
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
        res = track.create_report(TypingScreen.timer[self.timer_select_index])

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
    random_200_text = Handler_algo().predict_words()
    timer = [15, 30, 60]

    def __init__(self):
        self.no_chance = True
        super().__init__()
        uic.loadUi("practice.ui", self)

        # set username in account tab 
        # user_name = Login.get_userinfo().get("username")
        # self.account_btn.setText(user_name)



        self.treeWidget.clear()

        # timer option index    def selectTime
        self.timer_select_index = 0
        self.timer = PracticeScreen.timer[self.timer_select_index]
        # time counter

        self.timer_counter = PracticeScreen.timer[self.timer_select_index]

        self.test_button.clicked.connect(self.gotoHome)
        self.account_btn.clicked.connect(self.goto_account)
        self.tutor_btn.clicked.connect(lambda: widget.setCurrentIndex(widget.currentIndex() + 3))

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


    def showEvent(self,event):
        print("practicingscreen")
        if UserInfo.get_userinfo():
            self.account_btn.setText(UserInfo.get_userinfo().get("username"))
        super().showEvent(event)

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

        self.treeWidget.clear()
        #Handler_algo().predict_words()
        # hand.predict_words()

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
        cls.random_200_text = Handler_algo().predict_words()



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
        res = track.create_report(self.timer)


        for key,value in res.items():
            key_item = QTreeWidgetItem()
            key_item.setText(0,str(key))
            key_item.setText(1,str(value))
            self.treeWidget.addTopLevelItem(key_item)


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


        self.newpasswordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmpasswordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)

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
    #     def backToLoginScreen(self):  # from resetPasswordVerficadtionScreen logout = Logout()
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

        self.tutor_btn.clicked.connect(lambda: widget.setCurrentIndex(widget.currentIndex() + 2))

        self.load_reports()
        # Load reports on startup



    def showEvent(self,event):
        print("practicingscreen")
        if UserInfo.get_userinfo():
            self.account_btn.setText(UserInfo.get_userinfo().get("username"))
        super().showEvent(event)


        token = Login.is_authenticated()
        headers = {
            "Authorization":f"Bearer {token}"
        }


        user_info = requests.get("http://localhost:8000/user-info",headers = headers).json() 
        self.username_label.setText("Welcome " + user_info.get("username"))
        self.account_btn.setText(user_info.get("username"))
        self.email_label.setText("Email: " + user_info.get("email"))
        joined_date = user_info.get("create_at")
        joined_date_timezone = datetime.datetime.strptime(joined_date,"%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours = 5, minutes = 45)
        self.joinded_date_label.setText("Joinded Date: " + str(joined_date_timezone))

        test_taken = requests.get("http://localhost:8000/get-report",headers = headers).json()
        print("test_taken",len(test_taken))
        self.test_completed_label.setText("Test Taken: " + str(len(test_taken)))


        self.highest_wpm = [0, 0, 0]
        self.highest_rwpm = [0, 0, 0]
        self.accuracy = [0, 0, 0]

        
        for i in test_taken:
            second = i.get("second", 0)
            
            wpm = i.get("wpm")
            if wpm is not None:
                if second == 15 and wpm > self.highest_wpm[0]:
                    self.highest_wpm[0] = wpm
                elif second == 30 and wpm > self.highest_wpm[1]:
                    self.highest_wpm[1] = wpm
                elif second == 60 and wpm > self.highest_wpm[2]:
                    self.highest_wpm[2] = wpm
        
            rwpm = i.get("rwpm")
            if rwpm is not None:
                if second == 15 and rwpm > self.highest_rwpm[0]:
                    self.highest_rwpm[0] = rwpm
                elif second == 30 and rwpm > self.highest_rwpm[1]:
                    self.highest_rwpm[1] = rwpm
                elif second == 60 and rwpm > self.highest_rwpm[2]:
                    self.highest_rwpm[2] = rwpm
        
            acc = i.get("accuracy")
            if acc is not None:
                if second == 15 and acc > self.accuracy[0]:
                    self.accuracy[0] = acc
                elif second == 30 and acc > self.accuracy[1]:
                    self.accuracy[1] = acc
                elif second == 60 and acc > self.accuracy[2]:
                    self.accuracy[2] = acc

        print(self.highest_wpm)
        print(self.highest_rwpm)
        print(self.accuracy)


        row_position = self.tableWidget.rowCount()  # Get the current number of rows
        self.tableWidget.insertRow(row_position)    # Add a new empty row
        
        # Set items for the new row
        self.tableWidget.setItem(row_position, 0, QTableWidgetItem(str(self.highest_wpm[0])))
        self.tableWidget.setItem(row_position, 1, QTableWidgetItem(str(self.highest_wpm[1])))
        self.tableWidget.setItem(row_position, 2, QTableWidgetItem(str(self.highest_wpm[2])))
        
        # (Optional) If you want to add multiple rows for rwpm and accuracy:
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)
        self.tableWidget.setItem(row_position, 0, QTableWidgetItem(str(self.highest_rwpm[0])))
        self.tableWidget.setItem(row_position, 1, QTableWidgetItem(str(self.highest_rwpm[1])))
        self.tableWidget.setItem(row_position, 2, QTableWidgetItem(str(self.highest_rwpm[2])))
        
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)
        self.tableWidget.setItem(row_position, 0, QTableWidgetItem(str(self.accuracy[0])))
        self.tableWidget.setItem(row_position, 1, QTableWidgetItem(str(self.accuracy[1])))
        self.tableWidget.setItem(row_position, 2, QTableWidgetItem(str(self.accuracy[2])))








        timestamps = []
        wpm_values = []
        rwpm_values = []
        accuracy_values = []
        
        for report in test_taken:
            dt = datetime.datetime.fromisoformat(report['create_at'])
            timestamps.append(dt.timestamp())  # Convert datetime to float timestamp for plotting
            wpm_values.append(report['wpm'])
            rwpm_values.append(report['rwpm'])
            accuracy_values.append(report['accuracy'])
        
        # Convert to numpy arrays for better plotting performance
        x = np.array(timestamps)
        wpm = np.array(wpm_values)
        rwpm = np.array(rwpm_values)
        accuracy = np.array(accuracy_values)
        

        # Replace label_5 with pyqtgraph plot in QGridLayout
        label = self.findChild(QtWidgets.QLabel, "label_5")
        layout = label.parent().layout()
        
        # Find position of label_5 in the grid
        position = None
        for row in range(layout.rowCount()):
            for col in range(layout.columnCount()):
                item = layout.itemAtPosition(row, col)
                if item and item.widget() == label:
                    position = (row, col)
                    break
            if position:
                break
        
        if position:
            layout.removeWidget(label)
            label.deleteLater()
        
            graph_widget = pg.GraphicsLayoutWidget()
            layout.addWidget(graph_widget, position[0], position[1])
        
            # Add the plot
            plot = graph_widget.addPlot(title="WPM, RWPM, and Accuracy Over Time")
            plot.plot(x, wpm, pen=pg.mkPen('r', width=2), name="WPM")
            plot.plot(x, rwpm, pen=pg.mkPen('b', width=2), name="RWPM")
            plot.plot(x, accuracy, pen=pg.mkPen('g', width=2), name="Accuracy")
        
            plot.setLabel('left', 'Value')
            plot.setLabel('bottom', 'Time')
            plot.addLegend()
        
            axis = plot.getAxis('bottom')
            axis.setTicks([[(val, datetime.datetime.fromtimestamp(val).strftime('%H:%M:%S')) for val in x]])




        mistake = requests.get("http://localhost:8000/get-mistakes",headers = headers).json()
        print("mistakes",mistake)

        table = self.tableWidget_2
        table.setRowCount(len(mistake))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["key", "mistake", "missed"])

        for row, (key, value) in enumerate(mistake.items()):
            table.setItem(row, 0, QTableWidgetItem(str(key)))
            table.setItem(row, 1, QTableWidgetItem(str(value[0])))
            table.setItem(row, 2, QTableWidgetItem(str(value[1])))

        table.resizeColumnsToContents()





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




class Tutorial(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Tutor.ui", self)
        self.test_button.clicked.connect(lambda: widget.setCurrentIndex(widget.currentIndex() - 4))
        self.pushButton_2.clicked.connect(lambda: widget.setCurrentIndex(widget.currentIndex() - 3))
        self.account_btn.clicked.connect(lambda: widget.setCurrentIndex(widget.currentIndex() - 2))

        
        pairs = {
            # Home row
            'fj_btn': 'f-j',
            'dk_btn': 'd-k',
            'sl_btn': 's-l',
            'a;_btn': 'a-;',
            'gh_btn': 'g-h',
        
            # Top row
            'ru_btn': 'r-u',
            'ei_btn': 'e-i',
            'wo_btn': 'w-o',
            'qp_btn': 'q-p',
            'ty_btn': 't-y',
        
            # Bottom row
            'vn_btn': 'v-n',
            'cm_btn': 'c-m',
            'x,_btn': 'x-,',
            'z._btn': 'z-.',
            'b_btn': 'b',  # single letter drill
            'nm_btn': 'n-m',
        
            # Additional useful combos (optional but common)
            # 'ui_btn': 'u-i',
            # 'op_btn': 'o-p',
            # 'qw_btn': 'q-w',
            # 'as_btn': 'a-s',
            # 'zx_btn': 'z-x',
        }

        for btn_name, pair in pairs.items():
            btn = getattr(self, btn_name)
            btn.clicked.connect(lambda _, p=pair: self.open_key_tutorial({'pair': p}))

    def open_key_tutorial(self, lesson_data):
        tutorial_screen = KeyTutorial(lesson_data=lesson_data)
        widget.addWidget(tutorial_screen)
        widget.setCurrentWidget(tutorial_screen)

    def showEvent(self, event):
        print("tutorial")
        if UserInfo.get_userinfo():
            self.account_btn.setText(UserInfo.get_userinfo().get("username"))
        super().showEvent(event)


class KeyTutorial(QMainWindow):
    def __init__(self, lesson_data=None):
        super().__init__()
        uic.loadUi("key_tutor.ui", self)
        self.lesson_data = lesson_data

        try:
            self.go_back_tutorial.clicked.disconnect()
        except TypeError:
            pass  # no previous connection

        # Updated here: go back directly to the existing tutorial widget instance
        self.go_back_tutorial.clicked.connect(lambda: widget.setCurrentWidget(tutorial))
        self.test_type.textChanged.connect(self.textChangedfunc)


    def showEvent(self, event):
        super().showEvent(event)
        print("tutorial")
        # if UserInfo.get_userinfo():
        #     self.account_btn.setText(UserInfo.get_userinfo().get("username"))


        self.context:str = None
        self.intro: str = None

        lst = ['f-j', 'd-k', 's-l', 'a-;', 'g-h', 'r-u', 'e-i', 'w-o', 'q-p', 't-y', 'v-n', 'c-m', 'x-,', 'z-.', 'b', 'n-m']
        for i in lst:
            if i == self.lesson_data.get("pair"):
                with open("tutorials/" + i + ".txt","r") as file:
                    self.context = file.read()

                with open("tutorials/" + i + "_intro.txt","r") as file:
                    self.intro = file.read()

        if self.lesson_data.get("pair") == "j-f":
            self.active_key.setText("f and j key")

        self.textBrowser.setText(self.context)
        self.textBrowser_2.setText(self.intro)
        

        self.liveinput = LiveInputChecker(self.context,self.textBrowser)

    def textChangedfunc(self,strg):
        temp = strg
        input_check = self.liveinput.inputcheck(strg)

        if strg.endswith(" "):
            temp = strg
            self.liveinput.save_previous_word(temp)
            self.liveinput.wordindex += 1
            self.test_type.setText("")


if __name__ == "__main__":
    # Run the application
    app = QApplication([])

    # adding styling files
    with open("style/style.qss") as f:
        app.setStyleSheet(f.read())
    widget = QtWidgets.QStackedWidget()

    login = MyApp()
    resetConfirmation = ResetPasswordVerificationScreen()
    register = RegisterScreen()
    typingScreen = TypingScreen()
    practicescreen = PracticeScreen()
    accountscreen = AccountScreen()
    resetpassword = ResetPassword()
    tutorial = Tutorial()
    key_tutorial = KeyTutorial()

    widget.addWidget(login)
    widget.addWidget(register)
    widget.addWidget(resetConfirmation)
    widget.addWidget(typingScreen)
    widget.addWidget(practicescreen)
    widget.addWidget(accountscreen)
    widget.addWidget(resetpassword)
    widget.addWidget(tutorial)
    widget.addWidget(key_tutorial)

    widget.show()
    app.exec_()

