#  Carlos Garcia. Copyright (c) 2021.
#  This code is licensed under MIT license (see LICENSE file for details)
import sys
import calendar
from datetime import datetime, timedelta

import PyQt5.QtWidgets

from ui import Ui_PomodorWindow
from ui import Ui_pomodor_config
from controller import Controller


class Pomodor(PyQt5.QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(Pomodor, self).__init__(parent=parent)
        self.ui = Ui_PomodorWindow()
        self.ui.setupUi(self)
        self.__slots_intervals = 15
        self.__start_time = 1
        self.__break_time = 2
        self.ui.timer_lb.setText('Procrastination only leads to frustration')
        self.__controller = Controller(
            self.ui.timer_lcd,
            self.ui.session_img_lb,
            start_time=self.__start_time,
            break_time=self.__break_time,
        )

        # Connections
        self.ui.act_set_times.triggered.connect(self.__show_config)

        # Stylesheet
        self.setStyleSheet(
            """
                QTableWidget {
                 border-width: 3px;
                 border-style: solid;
                 border-radius: 6px;
                }
                QPushButton#start_btn {
                 background-color: red;
                border-style: outset;
                border-width: 2px;
                border-radius: 10px;
                border-color: beige;
                font: bold 14px;
                min-width: 10em;
                padding: 6px;
                }
            """
        )

        # Setting initial values
        self.__total_slots = int((60 / self.__slots_intervals) * 24)
        self.__set_table_labels()

        # Start Timer
        self.__controller.start_timer()

    def __set_table_labels(self):
        week_days = list(calendar.day_name)
        hour_list = self.__get_hours()
        hours = [hour.strftime('%I:%M %p') for hour in hour_list]
        self.ui.scheduler_table.setRowCount(self.__total_slots)
        self.ui.scheduler_table.setVerticalHeaderLabels(hours)
        self.ui.scheduler_table.setHorizontalHeaderLabels(week_days)

    def __get_hours(self):
        hours = []
        revert_time = 0
        today = datetime.now()
        current_min = today.minute
        if current_min != 0:
            while current_min % self.__slots_intervals != 0 and current_min > 0:
                current_min -= 1
                revert_time += 1
            today = today - timedelta(minutes=revert_time)

        for slot in range(0, self.__total_slots):
            hours.append(today + timedelta(minutes=self.__slots_intervals * slot))

        return hours

    def __show_config(self):
        self.config_dialog = PyQt5.QtWidgets.QDialog(parent=self)
        self.config_ui = Ui_pomodor_config()
        self.config_ui.setupUi(self.config_dialog)
        self.config_dialog.show()

        # connections
        self.config_ui.save_btn.clicked.connect(self.__save_config_file)
        self.config_ui.cancel_btn.clicked.connect(self.config_dialog.close)
        self.config_ui.quotes_search_btn.clicked.connect(self.__file_search)

    def __save_config_file(self):
        focus_time = self.config_ui.focus_time_sb.value()
        break_time = self.config_ui.break_time_sb.value()
        quotes_file = self.config_ui.quotes_file_txt.toPlainText()
        print(focus_time)
        print(break_time)
        print(quotes_file)

    def __file_search(self):
        file_path = PyQt5.QtWidgets.QFileDialog.getOpenFileName()[0]
        print('File Path --> {}'.format(file_path))
        if file_path:
            self.config_ui.quotes_file_txt.setText(file_path)


if __name__ == "__main__":
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    pomodor = Pomodor()
    pomodor.show()
    sys.exit(app.exec_())
