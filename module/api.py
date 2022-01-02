#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
handles api calls
"""
import requests
import config
import os
import json


def get_headers(conf: dict):
    """
    Build the header for the request
    :param conf: config dict
    :return: headers dict
    """
    headers = conf['API']['headers']
    return headers


def get_query(conf: dict, **kwargs):
    """
    Build the query for the request
    :param conf: config dict
    :return: query dict
    """
    token = conf['Login']['apitoken']
    params = conf['API']['params']

    if kwargs:
        page = kwargs.get('page')
        per_page = conf['API']['limit']
        query = {
            'token': token,
            'page': page,
            'per_page': per_page
        }
    else:
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


def get_info_api(conf: dict):
    """
    Generates a request to dump the collection value of user
    :param conf:
    :return: json and header info
    """
    url = conf['API']['release_url']
    url = url.replace('{username}', conf['Login']['username'])
    limit = conf['API']['limit']


def get_value_api(conf: dict):
    """
    Generates a request to dump the collection value info of user
    :param conf: configfile
    :return: json
    """
    url = conf['API']['value_url']
    url = url.replace('{username}', conf['Login']['username'])
    res = requests.request(
        'GET',
        url,
        params=get_query(conf),
        headers=get_headers(conf),
    )
    if res.status_code == 200:
        return json.loads(res.text.encode('utf-8'))
    else:
        raise ConnectionError


if __name__ == '__main__':
    root_dir = os.getcwd()
    root_dir = os.path.dirname(root_dir)
    configfile = config.read_config(os.path.join(root_dir, 'config/config.yaml'))
    # noinspection PyUnresolvedReferences
    username = configfile['Login']['username']
    # noinspection PyUnresolvedReferences
    token = configfile['Login']['apitoken']
    print(get_value_api(configfile))
