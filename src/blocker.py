#  Carlos Garcia. Copyright (c) 2021.
#  This code is licensed under MIT license (see LICENSE file for details)

# This code has been modified from https://github.com/Kalebu/Website-blocker-python/blob/master/app.py
import os
import json

from . import utils


class Blocker:

    window_host = r'C:\Windows\System32\drivers\etc\hosts'
    redirect_url = '127.0.0.1'

    def __init__(self):
        self.__sites_to_block = []
        self.update_sites()

    def block_sites(self):
        with open(self.window_host, "r+") as host_file:
            hosts = host_file.read()
            for site in self.__sites_to_block:
                if site not in hosts:
                    line_to_write = f'{self.redirect_url}              {site}\n'
                    host_file.write(line_to_write)

    def unblock_sites(self):
        with open(self.window_host, "r+") as host_file:
            hosts = host_file.readlines()
            host_file.seek(0)
            for host in hosts:
                if not any(site in host for site in self.__sites_to_block):
                    host_file.write(host)
            host_file.truncate()

    def update_sites(self):
        self.__sites_to_block = self.__get_sites_to_block()

    @staticmethod
    def __get_sites_to_block():
        config_data = utils.get_config_data()
        sites_names = config_data.get('sites', [])

        config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        sites_file_path = os.path.join(config_dir, 'sites.json')
        with open(sites_file_path, 'r') as sites_file:
            sites = json.load(sites_file)

        sites_to_block = []
        for siteName in sites_names:
            sites_to_block.extend(sites[siteName])

        return sites_to_block
