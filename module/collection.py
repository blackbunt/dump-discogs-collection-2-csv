#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dump Collection Info from Discogs API
"""
import os
import config
import login
import api


def setup_value_data(config_yaml: dict):
    """
    Returns a list which contains all the neccesary information for 'Show Library Statistics Menu'
    :param config_yaml:
    :return: list
    """
    info = {}
    liste = []
    req = api.get_collection_info(config_yaml)
    info['Username'] = config_yaml['Login']['username']
    info['Total items'] = req['pagination']['items']
    res = api.get_value_api(config_yaml)
    info['Min. Value'] = res['minimum']
    info['Med. Value'] = res['median']
    info['Max. Value'] = res['maximum']
    for key, value in info.items():
        liste.append(f'{key}: {value}')
    return liste




if __name__ == '__main__':
    root_dir = os.getcwd()
    root_dir = os.path.dirname(root_dir)
    configfile = config.read_config(os.path.join(root_dir, 'config/config.yaml'))
    infos = setup_value_data(configfile)
    print(infos)