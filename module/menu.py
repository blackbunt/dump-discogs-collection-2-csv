#!/usr/bin/env python
# -*- coding: utf-8 -*-
# handles menu rendering and menu config
from pick import pick
import yaml



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
def read_config(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def show_menu(configuration: dict, def_index=0):
    '''
    Renders a simple menu from input config
    :param def_index: position of indicator position, default value == 0
    :param configuration: a dict including a key title (str) and a key options (list)
    :return: list: option, index
    Returns a list with the chosen option and the index number of the input 'options' list
    '''
    if 'options' in configuration and 'title' in configuration:
        options = configuration['options']
        title = configuration['title']
        option, index = pick(options, title, indicator='•', default_index=def_index)
    else:
        raise TypeError("Missing key 'title' or missing key 'options'.")

    return [option, index]

def menu_main(menu_config_yaml: dict):
    '''
    Renders the main menu and execute the chosen options.
    :param menu_config_yaml: config from the menu.yaml key MainMenu
    :return: Nothing (Yet)
    '''
    config = menu_config_yaml['MainMenu']
    res = show_menu(config,)
    if res[0] == 0: # Run Data Dump 2 Excel File
        pass
    elif res[0] == 1: # Run Data Dunmp 2 CSV File
        pass
    elif res[0] == 2: # Run Show Library Statistics
        pass
    elif res[0] == 3: # Configure Login Data
        pass
    elif res[0] == 4: # Exit Program
        exit()
    else:
        raise RuntimeError('Should not be able to be here!')

if __name__ == '__main__':
    show_menu(main_menu)
