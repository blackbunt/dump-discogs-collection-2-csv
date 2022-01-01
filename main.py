#!/usr/bin/env python
# -*- coding: utf-8 -*-

from module import config, login, menu
import os
import sys

CONFIG_PATH = os.path.join(os.getcwd(), 'config/config.yaml')
MENU_PATH = os.path.join(os.getcwd(), 'config/menu.yaml')
# load general config file
# global gen_config
gen_config = config.read_config(CONFIG_PATH)
# load menu config file
menu_config = config.read_config(MENU_PATH)

# check if login data exists/connection is possible
if not login.check_login(gen_config, CONFIG_PATH):
    sys.exit('Connection to Discogs not possible.\nNo Network Connection?')
menu.menu_main(menu_config, gen_config, CONFIG_PATH)
