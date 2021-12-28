#!/usr/bin/env python
# -*- coding: utf-8 -*-
# handles login data
import os
import yaml
from menu import read_config
from api import login

def save_config(path, key):
    yaml_file = read_config(path)
    yaml_file
    yaml.dump(yaml_file, key)
def check_login(config_yaml: dict):
    handler = True
    if config_yaml['Login']['username'] is None:
        username: str = input('Please enter your Discogs username: ')
    if config_yaml['Login']['apitoken'] is None:
        apitoken: str = input('Please enter your Discogs apitoken: ')

    while handler:
        must_write = True
        #check if login is valid by login into discogs
        http_code =  login(username, apitoken, config_yaml)
        if http_code == 200:
            break
        elif http_code == 401:
            print('apitoken is invalid.\n')
            print(f'apitoken: {apitoken}\n')
            apitoken: str = input('Please reenter your Discogs apitoken: ')
        elif http_code == 400:
            print('username is invalid.\n')
            print(f'username: {username}')
            username: str = input('Please reenter your Discogs username: ')
        elif http_code == 502 | 503:
            raise ConnectionError(f'HTTP CODE: {http_code}')
        else:
            raise ConnectionError

    #elif config_yaml['Login']['username'] is str or config_yaml['Login']['apitoken'] is str:

if __name__ == '__main__':
    root_dir = os.getcwd().split('/module')
    config = read_config(os.path.join(root_dir[0], 'configuration/config.yaml'))
    check_login(config)