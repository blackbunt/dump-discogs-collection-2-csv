#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dump Collection Info from Discogs API
"""
import os
import config
import login
import api

def show_info(config_yaml: dict):




if __name__ == '__main__':
    root_dir = os.getcwd()
    root_dir = os.path.dirname(root_dir)
    configfile = config.read_config(os.path.join(root_dir, 'config/config.yaml'))
    print(login.check_login(configfile, os.path.join(root_dir, 'config/config.yaml')))