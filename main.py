#!/usr/bin/env python
# -*- coding: utf-8 -*-
import module
from module import menu
import os
# load general config
config = menu.read_config(os.path.join(os.getcwd(), 'config/config.yaml'))
# load menu Configuration
menus = menu.read_config(os.path.join(os.getcwd(), 'config/menu.yaml'))
# check if logindata exists


menu.menu_main(menus)
