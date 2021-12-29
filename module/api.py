#!/usr/bin/env python
# -*- coding: utf-8 -*-
# handles api calls
import requests
from module.menu import read_config
import os

def get_headers(config: dict):
    '''
    Build the header for the request
    :param config: config dict
    :return: headers dict
    '''
    headers = config['API']['headers']
    return headers


def get_query(config: dict):
    '''
    Build the query for the request
    :param config: config dict
    :return: query dict
    '''
    apitoken = config['Login']['apitoken']
    params = config['API']['params']

    token_key = config['API']['params']
    token_key = list(token_key.keys())[2]
    params.pop('token', None)
    token_entry = {token_key: apitoken}
    # merge dicts
    query = params | token_entry
    return query


def login(username: str, apitoken: str, config: dict):
    url = config['API']['release_url']
    url = url.replace('{username}', config['Login']['username'])
    res = requests.request(
        'GET',
        url,
        params=get_query(config),
        headers=get_headers(config),
    )
    http_code = res.status_code
    return http_code

if __name__ == '__main__':
    root_dir = os.getcwd()
    root_dir = os.path.dirname(root_dir)
    config = read_config(os.path.join(root_dir, 'config/config.yaml'))
    username = config['Login']['username']
    apitoken = config['Login']['apitoken']
    print(login(username, apitoken, config))

