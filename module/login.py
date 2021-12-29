#!/usr/bin/env python
# -*- coding: utf-8 -*-
# handles login data and checks if they are correct by logging into discogs
import os
import yaml
import sys
from module.menu import read_config
from module.api import login

# dummy code
def set_state(key: str, state: str, config_path: str):

    with open(config_path) as f:
        doc = yaml.safe_load(f)
    doc['state'] = state
    with open(config_path, 'w') as f:
        yaml.safe_dump(doc, f, default_flow_style=False)


def check_login(config_yaml: dict, config_path: str):
    '''
    Checks username, apitoken for correctness by contacting discogs api
    if the given values are not given or incorrect user input is required.
    The updated values are stored into the config.yaml file and the program reloads itself to reread the config file.
    :param config_yaml: config dict
    :param config_path: path to config str
    :return: bool True, only if success
    '''
    handler = True
    if config_yaml['Login']['username'] is None: # if username is missing in config
        username: str = input('Please enter your Discogs username: ')
        with open(config_path) as f:
            doc = yaml.safe_load(f)
        doc['Login']['username'] = username
        with open(config_path, 'w') as f:
            yaml.safe_dump(doc, f, default_flow_style=False)
            # flush opened files
            f.flush()
            # rerun script, to read in the config file
            os.execv(sys.executable, ['python'] + sys.argv)
    else: # if available in config
        username = config_yaml['Login']['username']

    if config_yaml['Login']['apitoken'] is None: # if apitoken is missing in config
        apitoken: str = input('Please enter your Discogs apitoken: ')
        with open(config_path) as f:
            doc = yaml.safe_load(f)
        doc['Login']['apitoken'] = apitoken
        with open(config_path, 'w') as f:
            yaml.safe_dump(doc, f, default_flow_style=False)
            # flush opened files
            f.flush()
            # rerun script, to read in the config file
            os.execv(sys.executable, ['python'] + sys.argv)
    else: # if available in config
        apitoken = config_yaml['Login']['apitoken']

    while handler:
        #check if login is valid by login into discogs
        http_code =  login(username, apitoken, config_yaml)
        if http_code == 200:
            break
        elif http_code == 401:
            print('apitoken is invalid.\n')
            print(f'apitoken: {apitoken}\n')
            apitoken: str = input('Please reenter your Discogs apitoken: ')
            with open(config_path) as f:
                doc = yaml.safe_load(f)
            doc['Login']['apitoken'] = apitoken
            with open(config_path, 'w') as f:
                yaml.safe_dump(doc, f, default_flow_style=False)
                # flush opened files
                f.flush()
                # rerun script, to read in the config file
                os.execv(sys.executable, ['python'] + sys.argv)
        elif http_code == 404:
            print('username is invalid.\n')
            print(f'username: {username}')
            username: str = input('Please reenter your Discogs username: ')
            with open(config_path) as f:
                doc = yaml.safe_load(f)
            doc['Login']['username'] = username
            with open(config_path, 'w') as f:
                yaml.safe_dump(doc, f, default_flow_style=False)
                # flush opened files
                f.flush()
                # rerun script, to read in the config file
                os.execv(sys.executable, ['python'] + sys.argv)
        elif http_code == 502 | 503:
            raise ConnectionError(f'Connection Error http code: {http_code}')
        else:
            raise BaseException(f'Some Error encountered http code: {http_code}')
    return True

    #elif config_yaml['Login']['username'] is str or config_yaml['Login']['apitoken'] is str:

if __name__ == '__main__':
    root_dir = os.getcwd()
    root_dir = os.path.dirname(root_dir)
    config = read_config(os.path.join(root_dir, 'config/config.yaml'))
    print(check_login(config, os.path.join(root_dir, 'config/config.yaml')))