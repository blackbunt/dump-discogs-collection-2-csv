#!/usr/bin/env python
# -*- coding: utf-8 -*-
import module
from module import menu, login
import os
import sys


CONFIG_PATH = os.path.join(os.getcwd(), 'config/config.yaml')
MENU_PATH = os.path.join(os.getcwd(), 'config/menu.yaml')
# load general config file
config = menu.read_config(CONFIG_PATH)
# load menu config file
menus = menu.read_config(MENU_PATH)

# check if logindata exists/connection is possible
if not login.check_login(config, CONFIG_PATH):
    sys.exit('Connection to Discogs not possible.\nNo Network Connection?')
menu.menu_main(menus)