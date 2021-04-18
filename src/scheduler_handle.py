#  Carlos Garcia. Copyright (c) 2021.
#  This code is licensed under MIT license (see LICENSE file for details)
from datetime import datetime, timedelta
from threading import Timer

from PyQt5 import QtCore

import utils


class SchedulerHandle(QtCore.QObject):

    INTERVAL_SEC = 60

    activate_timer = QtCore.pyqtSignal(str)
    show_message = QtCore.pyqtSignal(str)

    def __init__(self, slot_interval, schedule_info_lb):
        super(SchedulerHandle, self).__init__()
        self.__slot_interval = slot_interval
        self.__timer = Timer(1.0, self.check_time)
        self.__timer.start()
        self.__today_day = datetime.now().strftime("%A")
        self.__schedule_info_lb = schedule_info_lb

    def check_time(self):
        config_data = utils.get_config_data()
        schedule_day_hours = config_data['schedule_times'].get(self.__today_day, None)
        if not schedule_day_hours:
            self.show_message.emit('No hours have been set for today, use timer it manually.')
            return
        interval_time = self.is_valid_hour(schedule_day_hours)
        if not interval_time:
            self.activate_timer.emit('stop')
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
        selected_time = None
        is_valid = False
        interval_time = 0
        valid_counter = 1
        slot_sec_interval = self.__slot_interval * self.INTERVAL_SEC
        schedule_hours = sorted(schedule_day_hours)
        for index in range(len(schedule_hours)):
            hour, minutes = map(lambda value: int(value), schedule_hours[index].split(':'))
            time = datetime(current_time.year, current_time.month, current_time.day, hour, minutes)
            slot_time = time + timedelta(minutes=self.__slot_interval)

            if slot_time > time:
                delta = current_time - slot_time
                total_sec = delta.total_seconds()

                if total_sec < 0:
                    continue

                elif 0 < total_sec <= 900:
                    interval_time = delta.seconds
                    continue

            elif current_time < time:
                if selected_time:
                    delta = time - selected_time
                else:
                    delta = time - current_time
                total_sec = delta.total_seconds()
                if 0 < total_sec <= 900:
                    interval_time += total_sec
                    selected_time = time
                    continue
                else:
                    break









            # if not is_valid and current_time <= time:
            #     selected_time = current_time
            #     is_valid = True
            #     if index == len(schedule_hours) - 1:
            #         next_time = time + timedelta(minutes=self.__slot_interval)
            #     else:
            #         next_hour, next_minutes = map(lambda value: int(value), schedule_hours[index + 1].split(':'))
            #         next_time = datetime(current_time.year, current_time.month, current_time.day, next_hour,
            #                              next_minutes)
            #
            # if is_valid:
            #     dif_time =
            #
            #
            #
            #
            #     if delta.seconds == slot_sec_interval * valid_counter:
            #         print('In selected')
            #         valid_counter += 1
            #         continue
            #     elif delta.seconds > slot_sec_interval:
            #         print('In NOT selected')
            #         interval_time = delta.seconds
            #         break
            #     elif delta.seconds < slot_sec_interval:
            #         print('In selected')
            #         interval_time = delta.seconds
            #         break
            #     else:
            #         print('In else')
            #         interval_time = slot_sec_interval * valid_counter

        return interval_time
