#  Carlos Garcia. Copyright (c) 2021.
#  This code is licensed under MIT license (see LICENSE file for details)
import calendar
import os
import random
import sys
from collections import defaultdict
from datetime import datetime, timedelta

from PyQt5 import QtWidgets, QtGui

import src.admin
import src.utils
from src import Controller
from src import SchedulerHandle
from ui import Ui_PomodorWindow
from ui import Ui_pomodor_config


class Pomodor(QtWidgets.QMainWindow):

    SLOT_INTERVALS = 15
    BACKGROUND_COLOR = QtGui.QBrush(QtGui.QColor(0, 176, 224))
    WHITE_COLOR = QtGui.QBrush(QtGui.QColor("white"))

    def __init__(self, parent=None):
        super(Pomodor, self).__init__(parent=parent)
        self.ui = Ui_PomodorWindow()
        self.ui.setupUi(self)
        self.config_file_path = src.utils.get_config_file_path()
        self.__config_data = src.utils.get_config_data()

        # Connections
        self.ui.act_set_times.triggered.connect(self.__show_config)
        self.ui.reset_btn.clicked.connect(lambda: self.__update_timer(False))
        self.ui.stop_btn.clicked.connect(self.stop)
        self.ui.start_btn.clicked.connect(self.start)
        self.ui.switch_btn.clicked.connect(self.__switch_session)
        self.ui.save_schedule_btn.clicked.connect(self.__save_schedule_info)
        self.ui.save_apply_schedule_btn.clicked.connect(self.__save_apply_schedule)

        # Stylesheet
        style_sheet_file = os.path.join(os.path.dirname(self.config_file_path), 'style_sheet.txt')
        with open(style_sheet_file, 'r') as style_file:
            style_data = style_file.read()
        self.setStyleSheet(style_data)

        # Setting initial values
        self.__total_slots = int((60 / self.SLOT_INTERVALS) * 24)
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

        self.__scheduler_handle = SchedulerHandle(self.SLOT_INTERVALS, self.ui.scheduler_info_lb)
        self.__scheduler_handle.activate_timer.connect(self.__schedule_cmd)
        self.__scheduler_handle.show_message.connect(self.msg_dialog)

    @staticmethod
    def msg_dialog(msg, title='Pomodor'):
        msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, title, msg)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.exec()

    def stop(self):
        self.__controller.stop_timer()

    def start(self):
        self.__controller.start_timer()

    def is_running(self):
        return self.__controller.is_running()

    def __schedule_cmd(self, cmd):
        msg = None
        if cmd == 'start' and not self.is_running():
            self.start()
            msg = {
                'title': 'Pomodoro Schedule',
                'msg': 'Schedule time starts now!'
            }
        elif cmd == 'stop' and self.is_running():
            self.stop()
            msg = {
                'title': 'Pomodoro Schedule',
                'msg': 'No time schedule at this time. Timer has been stopped.'
            }
        if msg:
            self.__controller.notify(custom=msg)

    def __save_apply_schedule(self):
        self.__save_schedule_info()
        self.__scheduler_handle.restart_timer()

    def __switch_session(self):
        self.__controller.switch_session()

    def __set_schedule_table(self):
        week_days = list(calendar.day_name)
        hour_list = self.__get_hours()
        hours = [hour.strftime('%H:%M') for hour in hour_list]
        self.ui.scheduler_table.setRowCount(len(hours))
        self.ui.scheduler_table.setVerticalHeaderLabels(hours)
        self.ui.scheduler_table.setHorizontalHeaderLabels(week_days)
        self.__set_table_items()

    def __set_table_items(self):
        config_data = src.utils.get_config_data()
        total_columns = self.ui.scheduler_table.columnCount()
        total_rows = self.ui.scheduler_table.rowCount()
        for column in range(total_columns).__reversed__():
            for row in range(total_rows).__reversed__():
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

                new_item.setBackground(self.BACKGROUND_COLOR)

    def __save_schedule_info(self):
        config_data = src.utils.get_config_data()
        times_to_add = defaultdict(list)
        times_to_remove = defaultdict(list)
        for item in self.ui.scheduler_table.selectedItems():
            row_item = self.ui.scheduler_table.verticalHeaderItem(item.row())
            column_item = self.ui.scheduler_table.horizontalHeaderItem(item.column())
            hour = row_item.text()
            day = column_item.text()
            if item.background() == self.BACKGROUND_COLOR:
                times_to_remove[day].append(hour)
                item.setBackground(self.WHITE_COLOR)
            else:
                times_to_add[day].append(hour)
                item.setBackground(self.BACKGROUND_COLOR)

        for day, hours in times_to_add.items():
            if day not in config_data['schedule_times']:
                config_data['schedule_times'][day] = hours
            config_data['schedule_times'][day].extend(hours)

        for day, hours in times_to_remove.items():
            for hour in hours:
                config_data['schedule_times'][day].remove(hour)

        src.utils.save_config_data(config_data)
        self.ui.scheduler_table.clearSelection()
        self.msg_dialog('Schedule has been save.')

    def __get_hours(self):
        hours = []
        current_time = datetime.now()
        today = datetime(current_time.year, current_time.month, current_time.day, 9, 0)

        for slot in range(0, self.__total_slots):
            sc_time = today + timedelta(minutes=self.SLOT_INTERVALS * slot)
            if sc_time.hour == 23:
                break
            hours.append(sc_time)

        return hours

    def __show_config(self):
        self.config_dialog = QtWidgets.QDialog(parent=self)
        self.config_ui = Ui_pomodor_config()
        self.config_ui.setupUi(self.config_dialog)
        self.config_dialog.show()

        # Set initial values
        config_data = src.utils.get_config_data()
        if config_data:
            self.config_ui.focus_time_sb.setValue(config_data['focus_time'])
            self.config_ui.break_time_sb.setValue(config_data['break_time'])
            self.config_ui.quotes_file_txt.setText(config_data['quotes_file'])
            self.config_ui.facebook_cbx.setChecked('facebook' in config_data['sites'])
            self.config_ui.twitter_cbx.setChecked('twitter' in config_data['sites'])
            self.config_ui.youtube_cbx.setChecked('youtube' in config_data['sites'])

        # connections
        self.config_ui.save_btn.clicked.connect(self.__save_config_file)
        self.config_ui.cancel_btn.clicked.connect(self.config_dialog.close)
        self.config_ui.quotes_search_btn.clicked.connect(self.__file_search)
        self.config_ui.save_apply_btn.clicked.connect(lambda: self.__update_timer(True))

    def __save_config_file(self):
        config_data = src.utils.get_config_data()
        focus_time = self.config_ui.focus_time_sb.value()
        break_time = self.config_ui.break_time_sb.value()
        quotes_file = self.config_ui.quotes_file_txt.toPlainText()
        config_data['sites'] = []
        if self.config_ui.youtube_cbx.isChecked():
            config_data['sites'].append('youtube')
        if self.config_ui.twitter_cbx.isChecked():
            config_data['sites'].append('twitter')
        if self.config_ui.facebook_cbx.isChecked():
            config_data['sites'].append('facebook')
        config_data['focus_time'] = focus_time
        config_data['break_time'] = break_time
        config_data['quotes_file'] = quotes_file

        src.utils.save_config_data(config_data)
        self.config_dialog.close()

    def __update_timer(self, save):
        if save:
            self.__save_config_file()
        self.__focus_time, self.__break_time = self.__get_times()
        self.__controller.update_controller(self.__focus_time, self.__break_time)

    def __file_search(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName()[0]
        if file_path:
            self.config_ui.quotes_file_txt.setText(file_path)

    def __set_quote(self):
        config_data = src.utils.get_config_data()
        if not config_data:
            self.ui.timer_lb.setText('Procrastination only leads to frustration')
            return

        quotes_file_path = config_data['quotes_file']
        with open(quotes_file_path, 'r', encoding='utf8') as quote_file:
            quotes = quote_file.readlines()
        random_num = random.randint(0, len(quotes)-1)
        if random_num % 2 != 0:
            random_num -= 1

        quote = f'{quotes[random_num]}\n{quotes[random_num+1]}'
        if len(quotes[random_num]) > 180:
            font = self.ui.timer_lb.font()
            font.setPointSize(8)
            self.ui.timer_lb.setFont(font)
        self.ui.timer_lb.setText(quote)

    def __get_times(self):
        config_data = src.utils.get_config_data()
        if not config_data:
            self.__focus_time = 1
            self.__break_time = 2
            return

        self.__focus_time = config_data['focus_time']
        self.__break_time = config_data['break_time']

        return self.__focus_time, self.__break_time


def main():
    app = QtWidgets.QApplication(sys.argv)
    pomodor = Pomodor()
    pomodor.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    if not src.admin.is_user_admin():
        src.admin.run_win_as_admin(wait=False)
    else:
        main()
