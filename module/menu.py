#!/usr/bin/env python
# -*- coding: utf-8 -*-
# handles menu rendering and menu config
from pick import pick
from keyboard import wait
import yaml
import os

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

def not_implemented_yet():
    print('Not implemented yet. Continue with >Enter<')
    wait('Enter')

def read_config(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def show_menu(configuration: dict, def_index=0, def_back=False):
    '''
    Renders a simple menu from input config
    :param def_back: inserts a "Back to Menu option into the list at top, default is disabled
    :param def_index: position of indicator position, default value == 0
    :param configuration: a dict including a key title (str) and a key options (list)
    :return: list: option, index
    Returns a list with the chosen option and the index number of the input 'options' list
    '''
    if 'options' in configuration and 'title' in configuration:
        options = configuration['options']
        if True == def_back:
            options.insert(0, 'Back to Main Menu')
        title = configuration['title']
        option, index = pick(options, title, indicator='•', default_index=def_index)
    else:
        raise TypeError("Missing key 'title' or missing key 'options'.")

    return [option, index]


def menu_login_data(menu_config_yaml: dict):
    '''
    Renders the Configure Login Data Menu and execute the chosen options.
    :param menu_config_yaml: config from the menu.yaml key LoginData
    :return:
    '''
    config = menu_config_yaml['LoginData']
    res = show_menu(config, 0, True)
    if res[1] == 0:  # Back to Main Menu
        menu_main(menu_config_yaml)
    elif res[1] == 1:  # change username
        not_implemented_yet()
    elif res[1] == 2:  # change apitoken
        not_implemented_yet()
    else:
        raise RuntimeError('Should not be able to be here!')


def menu_main(menu_config_yaml: dict):
    '''
    Renders the main menu and execute the chosen options.
    :param menu_config_yaml: config from the menu.yaml key MainMenu
    :return: Nothing (Yet)
    '''
    config = menu_config_yaml['MainMenu']
    res = show_menu(config, 0)
    if res[1] == 0:  # Run Data Dump 2 Excel File
        not_implemented_yet()
    elif res[1] == 1:  # Run Data Dunmp 2 CSV File
        not_implemented_yet()
    elif res[1] == 2:  # Run Show Library Statistics
        not_implemented_yet()
    elif res[1] == 3:  # Configure Login Data
        menu_login_data(menu_config_yaml)
    elif res[1] == 4:  # Exit Program
        exit()
    else:
        exit()


if __name__ == '__main__':
    root_dir = os.getcwd()
    root_dir = os.path.dirname(root_dir)
    configfile = read_config(os.path.join(root_dir, 'config/menu.yaml'))
    # print(configfile)
    menu_main(configfile)

    #menu_login_data(configfile)
