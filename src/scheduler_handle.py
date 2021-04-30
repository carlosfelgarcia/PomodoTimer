#  Carlos Garcia. Copyright (c) 2021.
#  This code is licensed under MIT license (see LICENSE file for details)
from datetime import datetime, timedelta
from threading import Timer

from PyQt5 import QtCore

from . import utils


class SchedulerHandle(QtCore.QObject):

    INTERVAL_SEC = 60

    activate_timer = QtCore.pyqtSignal(str)
    show_message = QtCore.pyqtSignal(str)

    def __init__(self, slot_interval, schedule_info_lb):
        super(SchedulerHandle, self).__init__()
        self.__slot_interval = slot_interval
        self.__timer = Timer(0.01, self.check_time)
        self.__timer.start()
        self.__today_day = datetime.now().strftime("%A")
        self.__schedule_info_lb = schedule_info_lb

    def restart_timer(self):
        if self.__timer.is_alive():
            self.__timer.cancel()

        self.__timer = Timer(0.01, self.check_time)
        self.__timer.start()

    def check_time(self):
        config_data = utils.get_config_data()
        schedule_day_hours = config_data['schedule_times'].get(self.__today_day, None)
        if not schedule_day_hours:
            self.show_message.emit('No hours have been set for today, use timer it manually.')
            self.__schedule_info_lb.setText('Running on manual mode')
            return
        interval_time, cmd = self.is_valid_hour(schedule_day_hours)

        if cmd == 'stop':
            self.activate_timer.emit('stop')
            if not interval_time:
                self.__schedule_info_lb.setText('No time set on the schedule for the rest of the day. Running manual.')
                return
        else:
            self.activate_timer.emit('start')

        show_time = datetime.now() + timedelta(seconds=interval_time)
        show_time = show_time.strftime('%H:%M')
        msg = f'The scheduler will take over at {show_time}'
        self.__schedule_info_lb.setText(msg)

        self.__timer = Timer(interval_time, self.check_time)
        self.__timer.start()

    def is_valid_hour(self, schedule_day_hours):
        current_time = datetime.now()
        is_valid = False
        interval_time = 0
        cmd = 'stop'
        schedule_hours = sorted(schedule_day_hours)
        for index in range(len(schedule_hours)):
            hour, minutes = map(lambda value: int(value), schedule_hours[index].split(':'))
            time = datetime(current_time.year, current_time.month, current_time.day, hour, minutes)
            slot_time = time + timedelta(minutes=self.__slot_interval)

            if time <= current_time <= slot_time and not is_valid:
                is_valid = True

            if is_valid:
                str_slot_time = f'{slot_time.hour:02}:{slot_time.minute:02}'
                if str_slot_time not in schedule_hours:
                    delta = slot_time - current_time
                    interval_time = delta.total_seconds()
                    cmd = 'start'
                    break

        if not interval_time:
            for index in range(len(schedule_hours)):
                hour, minutes = map(lambda value: int(value), schedule_hours[index].split(':'))
                time = datetime(current_time.year, current_time.month, current_time.day, hour, minutes)
                if current_time < time:
                    delta = time - current_time
                    interval_time = delta.total_seconds()
                    break

        return interval_time, cmd
