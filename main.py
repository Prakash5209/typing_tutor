from typing import Dict
import module1
import pyqtgraph as pg
from inputchecker import LiveInputChecker,Fingers
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
from algo_handler import Handler_algo
import numpy as np
import json
import sys
import time

from ui import login,account,home,key_tutor,practice,register

temp: str = ""


sync_profile_info: Dict = None

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
    def __init__(self, stacked_widget):
        super().__init__()
        uic.loadUi("ui/login.ui", self)
        self.stacked_widget = stacked_widget  # Store widget reference

        self.login_button.clicked.connect(self.goto_homeScreen)
        self.pushButton_2.clicked.connect(self.goto_registerScreen)
        self.forgotPassword_btn.clicked.connect(self.goto_resetPasswordVerificationScreen)
        self.passwordlineEdit.setEchoMode(QtWidgets.QLineEdit.Password)

        QTimer.singleShot(0, self.auto_login_if_token_valid)

    def auto_login_if_token_valid(self):
        if Login.is_authenticated():
            print("Token valid. Redirecting to TypingScreen.")
            self.goto_typing_screen()
        else:
            print("Token not found or invalid.")

    def goto_registerScreen(self):
        register_screen = RegisterScreen(self.stacked_widget)
        self.stacked_widget.addWidget(register_screen)
        self.stacked_widget.setCurrentWidget(register_screen)

    def goto_resetPasswordVerificationScreen(self):
        reset_verification = ResetPasswordVerificationScreen(self.stacked_widget)
        self.stacked_widget.addWidget(reset_verification)
        self.stacked_widget.setCurrentWidget(reset_verification)

    def goto_homeScreen(self):
        username = self.usernamelineEdit.text()
        password = self.passwordlineEdit.text()
        login = Login(username, password)
        response_status = login.get_user()
        response_txt = json.loads(response_status.text)
        try:
            if response_status.status_code == 200 and response_txt.get("verified_user"):
                self.goto_typing_screen()
            elif response_status.status_code == 200 and not response_txt.get("verified_user"):
                self.goto_resetPasswordVerificationScreen()
        except Exception as e:
            print("Login failed:", e)

    def goto_typing_screen(self):
        typing_screen = TypingScreen(self.stacked_widget)
        self.stacked_widget.addWidget(typing_screen)
        self.stacked_widget.setCurrentWidget(typing_screen)


class RegisterScreen(QMainWindow):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        uic.loadUi("ui/register.ui", self)

        self.password_lineEdit_3.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_password_lineEdit_4.setEchoMode(QtWidgets.QLineEdit.Password)

        self.create_account_button.clicked.connect(self.create_account_button_function)
        self.register_b_login.clicked.connect(self.goto_login_screen)

    def create_account_button_function(self):
        email = self.email_lineEdit.text()
        username = self.username_lineEdit_2.text()
        password = self.password_lineEdit_3.text()
        confirm_password = self.confirm_password_lineEdit_4.text()

        r = Register(email, username, password, confirm_password)
        returned_info = r._Register__register_new_account()

        if returned_info == 201:
            # Assume next screen is TypingScreen or similar
            typing_screen = TypingScreen(self.stacked_widget)
            self.stacked_widget.addWidget(typing_screen)
            self.stacked_widget.setCurrentWidget(typing_screen)

    def goto_login_screen(self):
        login_screen = MyApp(self.stacked_widget)
        self.stacked_widget.addWidget(login_screen)
        self.stacked_widget.setCurrentWidget(login_screen)


class TypingScreen(QMainWindow):
    timer = [15, 30, 60]

    def __init__(self,stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.no_chance = True

        uic.loadUi("ui/home.ui", self)


        self.random_200_text = module1.typing_test_words()

        # timer option index
        self.timer_select_index = 0
        self.timer = TypingScreen.timer[self.timer_select_index]

        # time counter
        self.timer_counter = TypingScreen.timer[self.timer_select_index]

        self.practice_button.clicked.connect(self.gotoPractice)

        self.account_btn.clicked.connect(self.gotoAccount)
        self.test_type.textChanged.connect(self.textChangedfunc)
        self.test_refresh_button.clicked.connect(self.refresh_typing_text)

        # self.tutor_btn.clicked.connect(lambda: widget.setCurrentIndex(widget.currentIndex() + 4))
        self.tutor_btn.clicked.connect(self.gototutor)



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

        token = Login.is_authenticated()
        headers = {
            "Authorization":f"Bearer {token}"
        }
        try:
            user_profile_request = requests.get("http://localhost:8000/user-info",headers = headers)
            sync_profile_info = json.loads(user_profile_request.text)
        except Exception as e:
            print("sync_profile_info ",e)


        print("typingscreen")
        if UserInfo.get_userinfo():
            # self.account_btn.setText(UserInfo.get_userinfo().get("username")+ " xp: " +sync_profile_info.get("xp"))
            self.account_btn.setText(UserInfo.get_userinfo().get("username") + " " + str(sync_profile_info.get('xp')) + " xp")
            # self.account_btn.setText(sync_profile_info.get("xp",0))
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

    def gototutor(self):
        self.thread_cleanup()
        self.timer_counter = 0
        tutor_screen = Tutorial(self.stacked_widget)
        self.stacked_widget.addWidget(tutor_screen)
        self.stacked_widget.setCurrentWidget(tutor_screen)
        # widget.setCurrentIndex(widget.currentIndex() + 4)

    def gotoPractice(self):
        self.thread_cleanup()
        self.timer_counter = 0
        practice_screen = PracticeScreen(self.stacked_widget)
        self.stacked_widget.addWidget(practice_screen)
        self.stacked_widget.setCurrentWidget(practice_screen)

    def gotoAccount(self):
        self.thread_cleanup()
        self.timer_counter = 0
        account_screen = AccountScreen(self.stacked_widget)
        self.stacked_widget.addWidget(account_screen)
        self.stacked_widget.setCurrentWidget(account_screen)

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


    def assign_random_text(self):
        self.random_200_text = module1.typing_test_words()

    def textChangedfunc(self, strg):

        # print("is_authenticated", Login.is_authenticated())
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
        track = Tracker(self.random_200_text,raw_user_lst)
        track.track_characters()
        res = track.create_report(PracticeScreen.timer[self.timer_select_index])

        # print("res",res)
        with open(res.get("file_path"),"r") as f:
            mistakes = f.read()

        for key, value in res.items():
            key_item = QTreeWidgetItem()
            key_item.setText(0, str(key))
            key_item.setText(1, str(value))
            self.treeWidget.addTopLevelItem(key_item)

        mistakes = json.loads(mistakes).get("mistakes")

        for i in range(len(mistakes)):
            child_item = QTreeWidgetItem([str(mistakes[i])])
            self.treeWidget.addTopLevelItem(child_item)


        self.test_type.setEnabled(False)
        self.worker = None


class PracticeScreen(QMainWindow):

    timer = [15, 30, 60]

    def __init__(self,stacked_widget):
        self.no_chance = True
        super().__init__()

        self.stacked_widget = stacked_widget

        uic.loadUi("ui/practice.ui", self)


        # generate random words from xp
        token = Login.is_authenticated()
        headers = {
            "Authorization":f"Bearer {token}",
        }
        res_xp = 0
        try:
            res = requests.get("http://localhost:8000/user-info",headers = headers)
            res_xp = json.loads(res.text).get("xp",0)
        except Exception as e:
            print(e)

        size_word = 0
        if res_xp >= 100:
            size_word = 1000
        elif res_xp >= 70:
            size_word = 300
        elif res_xp >= 50:
            size_word = 100
        elif res_xp >= 30:
            size_word =50 
        elif res_xp >= 0:
            size_word = 30

        self.random_200_text = Handler_algo().predict_words(size_word)


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
        # self.tutor_btn.clicked.connect(lambda: widget.setCurrentIndex(widget.currentIndex() + 3))
        self.tutor_btn.clicked.connect(self.tutor)

        self.lineEdit.textChanged.connect(self.textChangedfunc)
        self.practice_refresh.clicked.connect(self.refresh_typing_text)


        # change the timer options in gui

        self.time_button.setText(
            f"time: {PracticeScreen.timer[self.timer_select_index]}")
        self.time_button.clicked.connect(self.selectTime)

        self.timer_thread = None
        self.worker = None

        self.practiceTextBrowser.setMarkdown(self.random_200_text)

        self.liveinput = LiveInputChecker(
            self.random_200_text, self.practiceTextBrowser)

        self.update_time = QTimer(self)
        self.update_time.timeout.connect(self.tracktimer)
        self.timer_started = False


    def showEvent(self,event):
        print("practicingscreen")
        token = Login.is_authenticated()
        headers = {
            "Authorization":f"Bearer {token}"
        }
        try:
            user_profile_request = requests.get("http://localhost:8000/user-info",headers = headers)
            sync_profile_info = json.loads(user_profile_request.text)
        except Exception as e:
            print("sync_profile_info ",e)

        if UserInfo.get_userinfo():
            # self.account_btn.setText(UserInfo.get_userinfo().get("username")+ " xp: " +sync_profile_info.get("xp"))
            self.account_btn.setText(UserInfo.get_userinfo().get("username") + " " + str(sync_profile_info.get('xp')) + " xp")
            # self.account_btn.setText(sync_profile_info.get("xp",0))

        super().showEvent(event)

    def tutor(self):
        self.thread_cleanup()
        self.timer_counter = 0
        tutor = Tutorial(self.stacked_widget)
        self.stacked_widget.addWidget(tutor)
        self.stacked_widget.setCurrentWidget(tutor)
        # self.stacked_widget.setCurrentIndex(tutor)
        # widget.setCurrentIndex(widget.currentIndex() + 3)

    def gotoHome(self):
        # thread cleaning
        self.thread_cleanup()
        self.timer_counter = 0
        home_screen = TypingScreen(self.stacked_widget)
        self.stacked_widget.addWidget(home_screen)
        self.stacked_widget.setCurrentWidget(home_screen)
        # widget.setCurrentIndex(widget.currentIndex() - 1)

    def goto_account(self):
        # thread cleaning
        self.thread_cleanup()
        self.timer_counter = 0
        account = AccountScreen(self.stacked_widget)
        self.stacked_widget.addWidget(account)
        self.stacked_widget.setCurrentWidget(account)



    def selectTime(self):
        if self.timer_select_index >= len(PracticeScreen.timer)-1:

            self.timer_select_index = 0
        else:
            self.timer_select_index += 1

        if not Worker.status:
            self.timer_counter = PracticeScreen.timer[self.timer_select_index]
            Worker.change_typing_time(
                finish_time=PracticeScreen.timer[self.timer_select_index])
            self.time_button.setText(
                f"time: {PracticeScreen.timer[self.timer_select_index]}")

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
            "time: "+str(PracticeScreen.timer[self.timer_select_index]))

        # enable the linedit after refreshing the
        self.lineEdit.setEnabled(True)

        # resetting self.timer_counter by assigning timer_counter to 0
        self.timer_counter = PracticeScreen.timer[self.timer_select_index]

        # self.random_200_text = module1.typing_test_words()
        self.assign_random_text()

        # self.filter_save
        # self.filter_save = Filter_and_save(self.random_200_text)

        # send to typing_test_words_from_TypingScreen
        self.liveinput = LiveInputChecker(
            self.random_200_text, self.practiceTextBrowser)

        self.practiceTextBrowser.setMarkdown(self.random_200_text)

        # clearing the input fields when refreshing the text
        self.lineEdit.blockSignals(True)
        self.lineEdit.setText("")
        self.lineEdit.blockSignals(False)

        # stop the worker thread when words is finished
        Worker.change_typing_time(finish_time=25)

        self.thread_cleanup()

    def assign_random_text(self):
        token = Login.is_authenticated()
        headers = {
            "Authorization":f"Bearer {token}",
        }
        try:
            res = requests.get("http://localhost:8000/user-info",headers = headers)
            res_xp = json.loads(res.text).get("xp",0)
        except Exception as e:
            print(e)

        size_word = 0
        if res_xp >= 100:
            size_word = 1000
        elif res_xp >= 70:
            size_word = 300
        elif res_xp >= 50:
            size_word = 100
        elif res_xp >= 30:
            size_word =50 
        elif res_xp >= 0:
            size_word = 30


        self.random_200_text = Handler_algo().predict_words(n_neighbors = size_word)



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
                        self.timer_counter = PracticeScreen.timer[self.timer_select_index]

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
        track = Tracker(self.random_200_text,raw_user_lst)
        track.track_characters()
        res = track.create_report(self.timer)

        with open(res.get("file_path"),"r") as f:
            mistakes = f.read()

        for key,value in res.items():
            key_item = QTreeWidgetItem()
            key_item.setText(0,str(key))
            key_item.setText(1,str(value))
            self.treeWidget.addTopLevelItem(key_item)

        mistakes = json.loads(mistakes).get("mistakes")

        for i in range(len(mistakes)):
            child_item = QTreeWidgetItem([str(mistakes[i])])
            self.treeWidget.addTopLevelItem(child_item)

        # disable the lineedit
        self.lineEdit.setEnabled(False)
        self.worker = None


class ResetPasswordVerificationScreen(QMainWindow):
    def __init__(self):
        self.obj = None
        super().__init__()
        uic.loadUi("ui/forgotPasswordVerificationCode.ui", self)

        # back to login screen from resetPasswordVerficadtionScreen
        self.forgotPasswordCancel_btn.clicked.connect(self.backToLoginScreen)
        self.send_code_to_email_pushButton_2.clicked.connect(
            self.send_code_to_email)
        self.recovery_code_submit.clicked.connect(
            self.confirm_recovery_code_func)

    def backToLoginScreen(self):  # from resetPasswordVerficadtionScreen

        widget.setCurrentIndex(widget.currentIndex() - 2)

    def send_code_to_email(self):
        email = self.email_lineEdit.text()
        self.obj = Account_recovery(email)
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
        uic.loadUi("ui/password_reset.ui", self)
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
        obj = obj.create_new_password(self.verification_obj, new_pass, confirm_pass, verified_user = True)

        # if 200 send to login window
        if obj.status_code == 200:
            widget.setCurrentIndex(widget.currentIndex()-6)

class AccountScreen(QMainWindow):
    def __init__(self,stacked_widget):
        super().__init__()
        uic.loadUi("ui/account.ui", self)
        self.stacked_widget = stacked_widget

        self.logout_btn.clicked.connect(self.backToLoginScreen)

        # back to typing screen
        self.test_session.clicked.connect(self.typing_screen)

        # back to practice screen
        self.practice_button.clicked.connect(self.practice_screen)

        self.tutor_btn.clicked.connect(self.tutor_screen)


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
        
            self.graph_widget = pg.GraphicsLayoutWidget()
            self.graph_widget.setMinimumHeight(400)  # or any height you prefer
            layout.addWidget(self.graph_widget, position[0], position[1])

    def typing_screen(self):
        typing_screen = TypingScreen(self.stacked_widget)
        self.stacked_widget.addWidget(typing_screen)
        self.stacked_widget.setCurrentWidget(typing_screen)

    def practice_screen(self):
        typing_screen = PracticeScreen(self.stacked_widget)
        self.stacked_widget.addWidget(typing_screen)
        self.stacked_widget.setCurrentWidget(typing_screen)

    def tutor_screen(self):
        typing_screen = Tutorial(self.stacked_widget)
        self.stacked_widget.addWidget(typing_screen)
        self.stacked_widget.setCurrentWidget(typing_screen)

    def showEvent(self,event):
        print("account section")
        token = Login.is_authenticated()
        headers = {
            "Authorization":f"Bearer {token}"
        }
        try:
            user_profile_request = requests.get("http://localhost:8000/user-info",headers = headers)
            sync_profile_info = json.loads(user_profile_request.text)
        except Exception as e:
            print("sync_profile_info ",e)

        print(sync_profile_info)
        if UserInfo.get_userinfo():
            print("nothing to see here")
            # self.account_btn.setText(UserInfo.get_userinfo().get("username")+ " xp: " +sync_profile_info.get("xp"))
            self.account_btn.setText(UserInfo.get_userinfo().get("username") + " " + str(sync_profile_info.get('xp')) + " xp")
            # self.account_btn.setText(sync_profile_info.get("xp",0))


        user_info = requests.get("http://localhost:8000/user-info",headers = headers).json()
        self.username_label.setText("Welcome " + user_info.get("username") + " " + str(sync_profile_info.get("xp")) + " xp")
        # self.account_btn.setText(user_info.get("username"))
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


        self.tableWidget.setRowCount(0)
        self.tableWidget.insertRow(0)    # Add a new empty row
        row_position = 0
        # Set items for the new row
        self.tableWidget.setItem(row_position, 0, QTableWidgetItem(str(self.highest_wpm[0])))
        self.tableWidget.setItem(row_position, 1, QTableWidgetItem(str(self.highest_wpm[1])))
        self.tableWidget.setItem(row_position, 2, QTableWidgetItem(str(self.highest_wpm[2])))
        
        # (Optional) If you want to add multiple rows for rwpm and accuracy:
        # row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)
        self.tableWidget.setItem(row_position, 0, QTableWidgetItem(str(self.highest_rwpm[0])))
        self.tableWidget.setItem(row_position, 1, QTableWidgetItem(str(self.highest_rwpm[1])))
        self.tableWidget.setItem(row_position, 2, QTableWidgetItem(str(self.highest_rwpm[2])))
        
        row_position = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_position)
        self.tableWidget.setItem(row_position, 0, QTableWidgetItem(str(self.accuracy[0])))
        self.tableWidget.setItem(row_position, 1, QTableWidgetItem(str(self.accuracy[1])))
        self.tableWidget.setItem(row_position, 2, QTableWidgetItem(str(self.accuracy[2])))


        row_labels = ["RWPM", "WPM", "Accuracy"]
        self.tableWidget.setVerticalHeaderLabels(row_labels)

        # Load reports on startup
        self.load_mistakes()
        self.load_reports()
        self.load_graph()


    def load_graph(self):

        token = Login.is_authenticated()

        headers = {
            "Authorization":f"Bearer {token}"
        }

        test_taken = requests.get("http://localhost:8000/get-report",headers = headers).json()
        timestamps = []
        wpm_values = []
        rwpm_values = []
        accuracy_values = []
        
        for report in test_taken:
            dt = datetime.datetime.fromisoformat(report['create_at'])
            timestamps.append(dt.timestamp())
            wpm_values.append(report['wpm'])
            rwpm_values.append(report['rwpm'])
            accuracy_values.append(report['accuracy'])
        
        # Convert to numpy arrays for better plotting performance
        x = np.array(timestamps)
        wpm = np.array(wpm_values)
        rwpm = np.array(rwpm_values)
        accuracy = np.array(accuracy_values)


        self.graph_widget.clear()
        plot = self.graph_widget.addPlot(title="WPM, RWPM, and Accuracy Over Time")
        plot.addLegend()  # Add legend BEFORE plotting

        # Plot data with names to appear in the legend
        wpm_curve = plot.plot(x, wpm, pen=pg.mkPen('r', width=2), name="WPM")
        rwpm_curve = plot.plot(x, rwpm, pen=pg.mkPen('b', width=2), name="RWPM")
        acc_curve = plot.plot(x, accuracy, pen=pg.mkPen('g', width=2), name="Accuracy")


        plot.setLabel('left', 'Value')
        plot.setLabel('bottom', 'Time')
        plot.addLegend()

        axis = plot.getAxis('bottom')
        axis.setTicks([[(val, datetime.datetime.fromtimestamp(val).strftime('%H:%M:%S')) for val in x]])




    def load_mistakes(self):
        tk = Login.is_authenticated()
        headers = {
            "Authorization": f"Bearer {tk}",
            "Content-Type": "application/json"
        }

        mistake = requests.get("http://localhost:8000/get-mistakes",headers = headers).json()
        print("Mistake",mistake)
        if mistake != None:
            table = self.tableWidget_2
            table.setRowCount(len(mistake))
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["key", "mistake", "missed"])

            for row, (key, value) in enumerate(mistake.items()):
                table.setItem(row, 0, QTableWidgetItem(str(key)))
                table.setItem(row, 1, QTableWidgetItem(str(value[0])))
                table.setItem(row, 2, QTableWidgetItem(str(value[1])))

            table.resizeColumnsToContents()
        else:
            print("mistake is empty")





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
            with open(report.get('file_path'),"r") as f:
                jdata = json.load(f)
                mistakes = jdata.get("mistakes",[])
                for i in range(len(mistakes)):
                    print("test",mistakes[i])
                    child_item = QTreeWidgetItem([str(mistakes[i])])
                    item.addChild(child_item)
                    # for key,value in mistakes[i].items():
                    #     child_item = QTreeWidgetItem([f"{key}: {value}"])
                    #     item.addChild(child_item)
            self.treeWidget.addTopLevelItem(item)

    def backToLoginScreen(self):
        logout = Logout()
        logout.remove_token()
        login_screen = MyApp(self.stacked_widget)
        self.stacked_widget.addWidget(login_screen)
        self.stacked_widget.setCurrentWidget(login_screen)




class Tutorial(QMainWindow):
    def __init__(self,stacked_widget):
        super().__init__()
        uic.loadUi("ui/Tutor.ui", self)
        self.stacked_widget = stacked_widget

        self.test_button.clicked.connect(self.gotoTestScreen)
        self.pushButton_2.clicked.connect(self.gotoPracticeScreen)
        self.account_btn.clicked.connect(self.gotoAccountScreen)

        # self.test_button.clicked.connect(lambda: widget.setCurrentIndex(widget.currentIndex() - 4))
        # self.pushButton_2.clicked.connect(lambda: widget.setCurrentIndex(widget.currentIndex() - 3))
        # self.account_btn.clicked.connect(lambda: widget.setCurrentIndex(widget.currentIndex() - 2))

        
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
        }

        for btn_name, pair in pairs.items():
            btn = getattr(self, btn_name)
            btn.clicked.connect(lambda _, p=pair: self.open_key_tutorial({'pair': p}))


    def gotoAccountScreen(self):
        account_screen = AccountScreen(self.stacked_widget)
        self.stacked_widget.addWidget(account_screen)
        self.stacked_widget.setCurrentWidget(account_screen)


    def gotoTestScreen(self):
        test_screen = TypingScreen(self.stacked_widget)
        self.stacked_widget.addWidget(test_screen)
        self.stacked_widget.setCurrentWidget(test_screen)

    def gotoPracticeScreen(self):
        practice_screen = PracticeScreen(self.stacked_widget)
        self.stacked_widget.addWidget(practice_screen)
        self.stacked_widget.setCurrentWidget(practice_screen)

    def open_key_tutorial(self, lesson_data):
        tutorial_screen = KeyTutorial(self.stacked_widget,lesson_data=lesson_data)
        widget.addWidget(tutorial_screen)
        widget.setCurrentWidget(tutorial_screen)

    def showEvent(self, event):
        super().showEvent(event)
        print("tutorial")

        token = Login.is_authenticated()
        headers = {
            "Authorization":f"Bearer {token}"
        }
        try:
            user_profile_request = requests.get("http://localhost:8000/user-info",headers = headers)
            sync_profile_info = json.loads(user_profile_request.text)
        except Exception as e:
            print("sync_profile_info ",e)


        if UserInfo.get_userinfo():
            # self.account_btn.setText(UserInfo.get_userinfo().get("username")+ " xp: " +sync_profile_info.get("xp"))
            self.account_btn.setText(UserInfo.get_userinfo().get("username") + " " + str(sync_profile_info.get('xp')) + " xp")
            # self.account_btn.setText(sync_profile_info.get("xp",0))



class KeyTutorial(QMainWindow):
    def __init__(self,stacked_widget, lesson_data=None):
        super().__init__()
        uic.loadUi("ui/key_tutor.ui", self)
        self.stacked_widget = stacked_widget
        self.lesson_data = lesson_data

        self.lp_label.setStyleSheet("padding:5px;")

        try:
            self.go_back_tutorial.clicked.disconnect()
        except TypeError:
            pass

        tutor_screen = Tutorial(self.stacked_widget)
        widget.addWidget(tutor_screen)
        self.go_back_tutorial.clicked.connect(lambda: widget.setCurrentWidget(tutor_screen))
        self.test_type.textChanged.connect(self.textChangedfunc)

    def showEvent(self, event):
        super().showEvent(event)
        print("tutorial")

        token = Login.is_authenticated()
        headers = {
            "Authorization":f"Bearer {token}"
        }
        try:
            user_profile_request = requests.get("http://localhost:8000/user-info",headers = headers)
            sync_profile_info = json.loads(user_profile_request.text)
        except Exception as e:
            print("sync_profile_info ",e)



        self.context: str = None
        self.intro: str = None

        lst = ['f-j', 'd-k', 's-l', 'a-;', 'g-h', 'r-u', 'e-i', 'w-o', 'q-p', 't-y', 'v-n', 'c-m', 'x-,', 'z-.', 'b', 'n-m']
        for i in lst:
            if i == self.lesson_data.get("pair"):
                with open("tutorials/" + i + ".txt", "r") as file:
                    self.context = file.read()
                with open("tutorials/" + i + "_intro.txt", "r") as file:
                    self.intro = file.read()

        if self.lesson_data.get("pair") == "j-f":
            self.active_key.setText("f and j key")

        self.textBrowser.setText(self.context)
        self.textBrowser_2.setText(self.intro)

        self.liveinput = LiveInputChecker(self.context, self.textBrowser)
        self.fingers = Fingers(self.context)

    
    def reset_all_labels(self):
        label_lst = ["lp_label", "lr_label", "lm_label", "li_label", 
                     "ri_label", "rm_label", "rr_label", "rp_label"]
        for label_name in label_lst:
            label = getattr(self, label_name, None)
            if label is not None:
                label.setStyleSheet("padding:5px;border-radius:5px")


    def textChangedfunc(self, strg):
        temp = strg
        input_check = self.liveinput.inputcheck(strg)
        future_key = self.fingers.userinput(strg)

        self.reset_all_labels()

        light_green = "background-color:#90EE90;padding:5px;border-radius:5px"
        light_blue = "background-color:#ADD8E6;padding:5px;border-radius:5px"

        if future_key in tuple("qaz"):
            self.lp_label.setStyleSheet(light_green)
        elif future_key in tuple("wsx"):
            self.lr_label.setStyleSheet(light_green)
        elif future_key in tuple("edc"):
            self.lm_label.setStyleSheet(light_green)
        elif future_key in tuple("rfvtgb"):
            self.li_label.setStyleSheet(light_green)
        elif future_key == "hit space":
            print("space")
        elif future_key in tuple("yhnujm"):
            self.ri_label.setStyleSheet(light_blue)
        elif future_key in tuple("ik,"):
            self.rm_label.setStyleSheet(light_blue)
        elif future_key in tuple("ol."):
            self.rr_label.setStyleSheet(light_blue)
        elif future_key in tuple("p;"):
            self.rp_label.setStyleSheet(light_blue)

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


    login = MyApp(widget)
    # resetConfirmation = ResetPasswordVerificationScreen()
    # register = RegisterScreen()
    # typingScreen = TypingScreen()
    # practicescreen = PracticeScreen()
    # accountscreen = AccountScreen()
    # resetpassword = ResetPassword()
    # tutorial = Tutorial()
    # key_tutorial = KeyTutorial()

    widget.addWidget(login)
    # widget.addWidget(register)
    # widget.addWidget(resetConfirmation)
    # widget.addWidget(typingScreen)
    # widget.addWidget(practicescreen)
    # widget.addWidget(accountscreen)
    # widget.addWidget(resetpassword)
    # widget.addWidget(tutorial)
    # widget.addWidget(key_tutorial)


    widget.setCurrentWidget(login)
    widget.showMaximized()
    app.exec_()

