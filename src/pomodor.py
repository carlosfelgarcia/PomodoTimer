#  Carlos Garcia. Copyright (c) 2021.
#  This code is licensed under MIT license (see LICENSE file for details)
import sys
import calendar
from datetime import datetime, timedelta

import PyQt5.QtWidgets

from ui import Ui_PomodorWindow


class Pomodor(PyQt5.QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Pomodor, self).__init__(parent=parent)
        self.ui = Ui_PomodorWindow()
        self.ui.setupUi(self)
        self.__slots_intervals = 15

        self.__total_slots = int((60 / self.__slots_intervals) * 24)

        # Setting initial values
        self.__set_table_labels()

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


if __name__ == "__main__":
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    pomodor = Pomodor()
    pomodor.show()
    sys.exit(app.exec_())
