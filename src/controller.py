#  Carlos Garcia. Copyright (c) 2021.
#  This code is licensed under MIT license (see LICENSE file for details)
from PyQt5 import QtCore
from PyQt5 import QtGui
from win10toast import ToastNotifier


class Controller:

    START_SESSION = 0
    BREAK_SESSION = 1

    def __init__(self, lcd_timer, img_label, focus_time, break_time):
        self.__focus_time = focus_time
        self.__break_time = break_time
        self.__lcd_timer = lcd_timer
        self.__time_minutes = self.__focus_time
        self.__time_seconds = 0
        self.__session = self.START_SESSION
        self.__img_label = img_label
        self.__notification = ToastNotifier()

        # Initial Values
        time_to_display = f'{self.__time_minutes}:{self.__time_seconds:02}'
        self.__lcd_timer.display(time_to_display)

        self.__timer = QtCore.QTimer()
        self.__timer.timeout.connect(self.__update_lcd)

    def is_running(self):
        return self.__timer.isActive()

    def start_timer(self):
        self.__timer.start(1000)

    def stop_timer(self):
        self.__timer.stop()

    def get_session_status(self):
        return self.__session

    def switch_session(self):
        self.__time_seconds = 0
        self.__time_minutes = 0
        self.__update_lcd(notify=False)

    def update_controller(self, focus_time, break_time):
        self.__focus_time = focus_time
        self.__break_time = break_time
        self.__time_minutes = 0
        self.__time_seconds = 0
        self.__update_lcd(notify=False, change_session=False)
        self.start_timer()

    def notify(self, break_session=False, custom=None):
        if custom:
            tittle = custom['title']
            msg = custom['msg']
            icon_path = 'C:\\Repo\\Pomodor\\ui\\tomato.ico'

        elif break_session:
            tittle = 'Focus session is over! :D'
            msg = 'Focus session is over time, enjoy your break!.'
            icon_path = 'C:\\Repo\\Pomodor\\ui\\coffee.ico'
        else:
            tittle = 'Break session is over!'
            msg = 'Break session is over time to go back and work.'
            icon_path = 'C:\\Repo\\Pomodor\\ui\\focus.ico'

        self.__notification.show_toast(
            title=tittle,
            msg=msg,
            icon_path=icon_path,
            threaded=True
        )

    def __update_lcd(self, notify=True, change_session=True):
        self.__time_seconds -= 1
        if self.__time_seconds <= 0:
            self.__time_seconds = 59
            self.__time_minutes -= 1

        if self.__time_minutes < 0:
            self.__time_seconds = 0

            if self.__session == self.START_SESSION:
                if change_session:
                    self.__session = self.BREAK_SESSION
                    self.__time_minutes = self.__break_time
                else:
                    self.__time_minutes = self.__focus_time
            else:
                if change_session:
                    self.__session = self.START_SESSION
                    self.__time_minutes = self.__focus_time
                else:
                    self.__time_minutes = self.__break_time

            if notify:
                self.notify(self.__session == self.BREAK_SESSION)

        time_to_display = f'{self.__time_minutes}:{self.__time_seconds:02}'
        self.__lcd_timer.display(time_to_display)
        self.__update_icon()

    def __update_icon(self):
        if self.__session == self.START_SESSION:
            self.__img_label.setPixmap(QtGui.QPixmap(":/Session/focus.png"))
        else:
            self.__img_label.setPixmap(QtGui.QPixmap(":/Session/coffee.png"))
