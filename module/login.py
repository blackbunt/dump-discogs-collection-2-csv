#!/usr/bin/env python
# -*- coding: utf-8 -*-
# handles login data and checks if they are correct by logging into discogs
import os
import yaml
import os
import sys
import psutil
import logging
from keyboard import wait
import config
import module.api as api
import module.menu as menu




def restart(message: str):
    """Restarts the current program, with file objects and descriptors
       cleanup
    """
    try:
        p = psutil.Process(os.getpid())
        for handler in p.get_open_files() + p.connections():
            os.close(handler.fd)
    except Exception as e:
        pass
    print(message + '\n\nPlease restart Program.\n\n Continue with >Enter<')
    wait('Enter')
    exit()
    #python = sys.executable
    #os.execlp(python, python, *sys.argv)


def chg_username(config_path: str, username: str, show_menu: bool):
    """
    enters or changes username in config.yaml
    :param show_menu: flips the input of username on/off true ==> on
    :param config_path: file path to config.yaml
    :param username: entered username
    :return:
    """
    with open(config_path) as f:
        doc = yaml.safe_load(f)
    doc['Login']['username'] = username
    if show_menu:
        res = menu.menu_yes_no(f'Username: {username} \n\nChange it?')
        if res[1] == 1:
            return 1
        else:
            username = input('Please input new username: ')

    with open(config_path, 'w') as f:
        doc['Login']['username'] = username
        yaml.safe_dump(doc, f, default_flow_style=False)
        #print(f'Username {username} successfully set.\n\nContinue with Enter...')
        #wait('Enter')  # Wait until user hits enter
        restart(f"Username '{username}' set.'")


def chg_apitoken(config_path: str, apitoken: str, show_menu: bool):
    """
    enters or changes apitoken in config.yaml
    :param show_menu: flips the input of apitoken on/off true ==> on
    :param config_path: file path to config.yaml
    :param apitoken: entered apitoken
    :return:
    """
    with open(config_path) as f:
        doc = yaml.safe_load(f)
    doc['Login']['apitoken'] = apitoken
    if show_menu:
        res = menu.menu_yes_no(f"Apitoken:\n\n{apitoken} \n\nChange it?")
        if res[1] == 1:
            return 1
        else:
            apitoken = input(f'Please input new apitoken: ')
    with open(config_path, 'w') as f:
        doc['Login']['apitoken'] = apitoken
        yaml.safe_dump(doc, f, default_flow_style=False)
        print(f'Apitoken {apitoken} successfully set.\n\nContinue with Enter...')
        wait('Enter')  # Wait until user hits enter
        restart(f"Apitoken '{apitoken}' set.'")


def check_login(config_yaml: dict, config_path: str, **kwargs):
    """
    Checks username, apitoken for correctness by contacting discogs api
    if the given values are not given or incorrect user input is required.
    The updated values are stored into the config.yaml file and the program reloads itself to reread the config file.
    :param config_yaml: config dict
    :param config_path: path to config str
    :return: bool True, only if success
    """
    handler = True
    if config_yaml['Login']['username'] is None:  # if username is missing in config
        username: str = input('Please enter your Discogs username: ')
        chg_username(config_path, username, False)
    else:  # if available in config
        username = config_yaml['Login']['username']

    if config_yaml['Login']['apitoken'] is None:  # if apitoken is missing in config
        apitoken: str = input('Please enter your Discogs apitoken: ')
        chg_apitoken(config_path, apitoken, False)
    else:  # if available in config
        apitoken = config_yaml['Login']['apitoken']

    while handler:
        # check if login is valid by login into discogs
        if kwargs:
            username = kwargs.get('username')
            apitoken = kwargs.get('apitoken')
        http_code = api.login_api(username, apitoken, config_yaml)
        if http_code == 200:
            break
        elif http_code == 401:
            print('apitoken is invalid.\n')
            print(f'apitoken: {apitoken}\n')
            apitoken: str = input('Please reenter your Discogs apitoken: ')
            chg_apitoken(config_path, apitoken, False)
        elif http_code == 404 or http_code == 403:
            print('username is invalid.\n')
            print(f'username: {username}')
            username: str = input('Please reenter your Discogs username: ')
            chg_username(config_path, username, False)
        elif http_code == 502 or http_code == 503:
            raise ConnectionError(f'Connection Error http code: {http_code}')
        else:
            print(f'Some Error encountered http code: {http_code}')
    return True

    # elif config_yaml['Login']['username'] is str or config_yaml['Login']['apitoken'] is str:


if __name__ == '__main__':
    root_dir = os.getcwd()
    root_dir = os.path.dirname(root_dir)
    configfile = config.read_config(os.path.join(root_dir, 'config/config.yaml'))
    print(check_login(configfile, os.path.join(root_dir, 'config/config.yaml')))
