#!/usr/bin/env python
# -*- coding: utf-8 -*-
# handles api calls
import requests
import config
import os


def get_headers(conf: dict):
    """
    Build the header for the request
    :param conf: config dict
    :return: headers dict
    """
    headers = conf['API']['headers']
    return headers


def get_query(conf: dict):
    """
    Build the query for the request
    :param conf: config dict
    :return: query dict
    """
    token = conf['Login']['apitoken']
    params = conf['API']['params']

    conf_query = conf['API']['params']
    token_key = list(conf_query.keys())[2]
    params.pop('token', None)
    token_entry = {token_key: token}
    # merge dicts
    query = params | token_entry
    return query


def login_api(user: str, token: str, conf: dict):
    """
    Generates a request to test the login credentials
    :param conf: configfile
    :return: http code int
    """
    url = conf['API']['release_url']
    url = url.replace('{username}', conf['Login']['username'])
    res = requests.request(
        'GET',
        url,
        params=get_query(conf),
        headers=get_headers(conf),
    )
    http_code = res.status_code
    return http_code


if __name__ == '__main__':
    root_dir = os.getcwd()
    root_dir = os.path.dirname(root_dir)
    configfile = config.read_config(os.path.join(root_dir, 'config/config.yaml'))
    # noinspection PyUnresolvedReferences
    username = config['Login']['username']
    # noinspection PyUnresolvedReferences
    token = config['Login']['apitoken']
    print(login_api(configfile))
