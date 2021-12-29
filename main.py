#!/usr/bin/env python
# -*- coding: utf-8 -*-
import module
from module import menu, login
import os

CONFIG_PATH = os.path.join(os.getcwd(), 'config/config.yaml')
# load general config
config = menu.read_config(CONFIG_PATH)
# load menu Configuration
menus = menu.read_config(CONFIG_PATH)
# check if logindata exists
if login.check_login(config, CONFIG_PATH):
    print('Connection established.')
