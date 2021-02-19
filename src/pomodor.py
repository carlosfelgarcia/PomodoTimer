#  Carlos Garcia. Copyright (c) 2021.
#  This code is licensed under MIT license (see LICENSE file for details)
import sys
import calendar

import PyQt5.QtWidgets

from ui import Ui_PomodorWindow


class Pomodor(PyQt5.QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Pomodor, self).__init__(parent=parent)
        self.ui = Ui_PomodorWindow()
        self.ui.setupUi(self)

        # Setting initial values
        self.__set_table_labels()

    def __set_table_labels(self):
        week_days = list(calendar.day_name)
        self.ui.scheduler_table.setHorizontalHeaderLabels(week_days)


if __name__ == "__main__":
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    pomodor = Pomodor()
    pomodor.show()
    sys.exit(app.exec_())
