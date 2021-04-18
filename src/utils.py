#  Carlos Garcia. Copyright (c) 2021.
#  This code is licensed under MIT license (see LICENSE file for details)
import json
import os


def get_config_file_path():
    config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
    config_path = os.path.join(config_dir, 'pomodor.json')
    return config_path


def get_config_data():
    config_file_path = get_config_file_path()
    if not os.path.exists(config_file_path):
        return
    with open(config_file_path, 'r') as config_file:
        config_data = json.load(config_file)
    return config_data


def save_config_data(data_to_save):
    config_file_path = get_config_file_path()
    with open(config_file_path, 'w') as config_file:
        json.dump(data_to_save, config_file)
