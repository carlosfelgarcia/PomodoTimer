#  Carlos Garcia. Copyright (c) 2021.
#  This code is licensed under MIT license (see LICENSE file for details)
import sys
import os
import json
import random
import calendar
from datetime import datetime, timedelta
from collections import defaultdict

from PyQt5 import QtWidgets, QtCore


from ui import Ui_PomodorWindow
from ui import Ui_pomodor_config
from controller import Controller


class Pomodor(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(Pomodor, self).__init__(parent=parent)
        self.ui = Ui_PomodorWindow()
        self.ui.setupUi(self)
        self.config_file_path = self.__get_config_file_path()
        self.__config_data = self.__get_config_data()
        self.__slots_intervals = 15

        # Connections
        self.ui.act_set_times.triggered.connect(self.__show_config)
        self.ui.reset_btn.clicked.connect(lambda: self.__update_timer(False))
        self.ui.stop_btn.clicked.connect(self.__stop)
        self.ui.start_btn.clicked.connect(self.__start)
        self.ui.switch_btn.clicked.connect(self.__switch_session)
        self.ui.save_schedule_btn.clicked.connect(self.__save_schedule_info)

        # Stylesheet
        style_sheet_file = os.path.join(os.path.dirname(self.__get_config_file_path()), 'style_sheet.txt')
        with open(style_sheet_file, 'r') as style_file:
            style_data = style_file.read()
        self.setStyleSheet(style_data)

        # Setting initial values
        self.__total_slots = int((60 / self.__slots_intervals) * 24)
        self.__set_schedule_table()
        self.__set_quote()
        self.__focus_time, self.__break_time = self.__get_times()

        # Create support Classes
        self.__controller = Controller(
            self.ui.timer_lcd,
            self.ui.session_img_lb,
            focus_time=self.__focus_time,
            break_time=self.__break_time,
        )

        # Start Timer
        self.__controller.start_timer()

    def __switch_session(self):
        self.__controller.switch_session()

    def __stop(self):
        self.__controller.stop_timer()

    def __start(self):
        self.__controller.start_timer()

    def __set_schedule_table(self):
        week_days = list(calendar.day_name)
        hour_list = self.__get_hours()
        hours = [hour.strftime('%I:%M %p') for hour in hour_list]
        self.ui.scheduler_table.setRowCount(self.__total_slots)
        self.ui.scheduler_table.setVerticalHeaderLabels(hours)
        self.ui.scheduler_table.setHorizontalHeaderLabels(week_days)
        self.__set_table_items()

    def __set_table_items(self):
        config_data = self.__get_config_data()
        total_columns = self.ui.scheduler_table.columnCount()
        total_rows = self.ui.scheduler_table.rowCount()
        for column in range(total_columns):
            for row in range(total_rows):
                new_item = QtWidgets.QTableWidgetItem()
                self.ui.scheduler_table.setItem(row, column, new_item)
                schedule_times = config_data.get('schedule_times', None)
                if not schedule_times:
                    continue

                column_item = self.ui.scheduler_table.horizontalHeaderItem(column)
                day = column_item.text()
                day_hours = schedule_times.get(day, None)
                if not day_hours:
                    continue

                row_item = self.ui.scheduler_table.verticalHeaderItem(row)
                hour = row_item.text()
                if hour not in day_hours:
                    continue

                self.ui.scheduler_table.setCurrentItem(new_item, QtCore.QItemSelectionModel.Select)

    def __save_schedule_info(self):
        config_data = self.__get_config_data()
        selected_times = defaultdict(list)
        for item in self.ui.scheduler_table.selectedItems():
            row_item = self.ui.scheduler_table.verticalHeaderItem(item.row())
            column_item = self.ui.scheduler_table.horizontalHeaderItem(item.column())
            hour = row_item.text()
            day = column_item.text()
            selected_times[day].append(hour)
        config_data['schedule_times'] = selected_times
        self.__save_config_data(config_data)

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
        self.config_dialog = QtWidgets.QDialog(parent=self)
        self.config_ui = Ui_pomodor_config()
        self.config_ui.setupUi(self.config_dialog)
        self.config_dialog.show()

        # Set initial values
        config_data = self.__get_config_data()
        if config_data:
            self.config_ui.focus_time_sb.setValue(config_data['focus_time'])
            self.config_ui.break_time_sb.setValue(config_data['break_time'])
            self.config_ui.quotes_file_txt.setText(config_data['quotes_file'])

        # connections
        self.config_ui.save_btn.clicked.connect(self.__save_config_file)
        self.config_ui.cancel_btn.clicked.connect(self.config_dialog.close)
        self.config_ui.quotes_search_btn.clicked.connect(self.__file_search)
        self.config_ui.save_apply_btn.clicked.connect(lambda: self.__update_timer(True))

    def __save_config_file(self):
        settings_to_save = {}
        focus_time = self.config_ui.focus_time_sb.value()
        break_time = self.config_ui.break_time_sb.value()
        quotes_file = self.config_ui.quotes_file_txt.toPlainText()
        settings_to_save['focus_time'] = focus_time
        settings_to_save['break_time'] = break_time
        settings_to_save['quotes_file'] = quotes_file
        self.config_dialog.close()

    def __save_config_data(self, data_to_save):
        with open(self.config_file_path, 'w') as config_file:
            json.dump(data_to_save, config_file)

    def __update_timer(self, save):
        if save:
            self.__save_config_file()
        self.__focus_time, self.__break_time = self.__get_times()
        self.__controller.update_controller(self.__focus_time, self.__break_time)

    def __file_search(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName()[0]
        if file_path:
            self.config_ui.quotes_file_txt.setText(file_path)

    @staticmethod
    def __get_config_file_path():
        config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        config_path = os.path.join(config_dir, 'pomodor.json')
        return config_path

    def __set_quote(self):
        config_data = self.__get_config_data()
        if not config_data:
            self.ui.timer_lb.setText('Procrastination only leads to frustration')
            return

        quotes_file_path = config_data['quotes_file']
        with open(quotes_file_path, 'r', encoding='utf8') as quote_file:
            quotes = quote_file.readlines()
        random_num = random.randint(0, len(quotes)-1)
        if random_num % 2 == 0:
            random_num -= 1

        quote = f'{quotes[random_num]}\n{quotes[random_num+1]}'
        self.ui.timer_lb.setText(quote)

    def __get_times(self):
        config_data = self.__get_config_data()
        if not config_data:
            self.__focus_time = 1
            self.__break_time = 2
            return

        self.__focus_time = config_data['focus_time']
        self.__break_time = config_data['break_time']

        return self.__focus_time, self.__break_time

    def __get_config_data(self):
        if not os.path.exists(self.config_file_path):
            return
        with open(self.config_file_path, 'r') as config_file:
            config_data = json.load(config_file)
        return config_data


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    pomodor = Pomodor()
    pomodor.show()
    sys.exit(app.exec_())
