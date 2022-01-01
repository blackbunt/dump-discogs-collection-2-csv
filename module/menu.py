#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
renders menus from menu.yaml
"""
from pick import pick
from keyboard import wait
import os
import platform
import module.login as login
import config

#test dict
main_menu: dict = {
    'title': 'Discogs Library Dumper',
    'options': [
        'Dump Discogs Library to Excel File',
        'Dump Discogs Library to CSV File',
        'Show Library Statistics',
        'Configure Login Data',
        'Exit'
    ]
}


def clear_scr():
    system = platform.system()
    if system == 'Windows':
        clear = lambda: os.system('cls')
        clear
    elif system == 'Linux' or platform == 'Darwin':
        clear = lambda: os.system('clear')
        clear()
    else:
        pass
    return None


def not_implemented_yet():
    print('Not implemented yet. Continue with >Enter<')
    wait('Enter')


def show_menu(configuration: dict, def_index=0, def_back=False, **kwargs):
    """
    Renders a simple menu from input config
    :param def_back: inserts a "Back to Menu option into the list at top, default is disabled
    :param def_index: position of indicator position, default value == 0
    :param configuration: a dict including a key title (str) and a key options (list)
    **kwargs:
    'title' change title if Config is empty
    :return: list: option, index
    Returns a list with the chosen option and the index number of the input 'options' list
    """
    if 'options' in configuration and 'title' in configuration:
        options = configuration['options']
        # add Back to Main Menu Option
        if def_back:
            if options[0] != 'Back to Main Menu':
                options.insert(0, 'Back to Main Menu')
        title = configuration['title']
        # if title value in menu.yaml is None than use kwargs
        if title is None:
            title = kwargs.get('title')
        option, index = pick(options, title, indicator='•', default_index=def_index)
    else:
        raise TypeError("Missing key 'title' or missing key 'options'.")

    return [option, index]


def menu_yes_no(message: str):
    """
    Renders a yes/no option menu, returns choice
    :param message: message printed for decision
    :return:
    """
    conf = {
        'title': message,
        'options': [
            'Yes',
            'No'
        ]
    }
    res = show_menu(conf, 1, title=message)
    return res


def menu_login_data(menu_config_yaml: dict, gen_config_yaml: dict, gen_config_path: str):
    """
    Renders the Configure Login Data Menu and execute the chosen options.
    :param gen_config_path: str containing the path to config.yaml
    :param gen_config_yaml: config from the config.yaml
    :param menu_config_yaml: config from the menu.yaml key LoginData
    :return:
    """
    conf = menu_config_yaml['LoginData']
    res = show_menu(conf, 0, True)
    username = gen_config_yaml['Login']['username']
    apitoken = gen_config_yaml['Login']['apitoken']
    if res[1] == 0:  # Back to Main Menu
        menu_main(menu_config_yaml, gen_config_yaml, gen_config_path)
    elif res[1] == 1:  # change username
        res = login.chg_username(gen_config_path, username, True)
        # if nothing changed run menu_login_data again
        if res == 1:
            menu_login_data(menu_config_yaml, gen_config_yaml, gen_config_path)
        else:
            pass
    elif res[1] == 2:  # change apitoken
        res = login.chg_apitoken(gen_config_path, apitoken, True)
        # if nothing changed run menu_login_data again
        if res == 1:
            menu_login_data(menu_config_yaml, gen_config_yaml, gen_config_path)
        else:
            pass
    else:
        raise RuntimeError('Should not be able to be here!')


def menu_main(menu_config_yaml: dict, gen_config_yaml: dict, gen_config_path):
    """
    Renders the main menu and execute the chosen options.
    :param gen_config_path:
    :param gen_config_yaml: config from the config.yaml
    :param menu_config_yaml: config from the menu.yaml key MainMenu
    :return: Nothing (Yet)
    """
    config_file = menu_config_yaml['MainMenu']
    res = show_menu(config_file, 0)
    if res[1] == 0:  # Run Data Dump 2 Excel File
        not_implemented_yet()
    elif res[1] == 1:  # Run Data Dump 2 CSV File
        not_implemented_yet()
    elif res[1] == 2:  # Run Show Library Statistics
        not_implemented_yet()
    elif res[1] == 3:  # Configure Login Data
        menu_login_data(menu_config_yaml, gen_config_yaml, gen_config_path)
    elif res[1] == 4:  # Exit Program
        exit()
    else:
        exit()


if __name__ == '__main__':
    root_dir = os.getcwd()
    root_dir = os.path.dirname(root_dir)
    menu_configfile = config.read_config(os.path.join(root_dir, 'config/menu.yaml'))
    gen_configfile = config.read_config(os.path.join(root_dir, 'config/config.yaml'))
    # print(configfile)
    menu_main(menu_configfile, gen_configfile, 'config/config.yaml')

    # menu_login_data(configfile)
