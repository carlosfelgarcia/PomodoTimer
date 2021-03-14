#  Carlos Garcia. Copyright (c) 2021.
#  This code is licensed under MIT license (see LICENSE file for details)
from PyQt5 import QtCore
from PyQt5 import QtGui
from win10toast import ToastNotifier


class Controller:

    START_SESSION = 0
    BREAK_SESSION = 1

    def __init__(self, lcd_timer, img_label, start_time, break_time):
        self.__start_time = start_time
        self.__break_time = break_time
        self.__lcd_timer = lcd_timer
        self.__time = self.__start_time
        self.__session = self.START_SESSION
        self.__img_label = img_label
        self.__notification = ToastNotifier()

        # Initial Values
        self.__lcd_timer.display(self.__start_time)

        self.__timer = QtCore.QTimer()
        self.__timer.timeout.connect(self.update_lcd)

    def start_timer(self):
        self.__timer.start(10000)

    def get_session_status(self):
        return self.__session

    def notify(self, breakSession=False):
        if breakSession:
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

    def update_lcd(self):
        print('Time {}'.format(self.__time))
        if self.__session == self.START_SESSION:
            self.__time -= 1
            if self.__time == 0:
                self.__session = self.BREAK_SESSION
                self.__time = self.__break_time
                self.notify(breakSession=True)
        else:
            self.__time -= 1
            if self.__time == 0:
                self.__session = self.START_SESSION
                self.__time = self.__start_time
                self.notify()

        self.__lcd_timer.display(self.__time)
        self.__update_icon()

    def __update_icon(self):
        if self.__session == self.START_SESSION:
            self.__img_label.setPixmap(QtGui.QPixmap(":/Session/focus.png"))
        else:
            self.__img_label.setPixmap(QtGui.QPixmap(":/Session/coffee.png"))
