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
        conf_query = {
            'token': token,
            'page': page,
            'per_page': per_page
        }
    else:
        conf_query = conf['API']['params']
        conf_query['token'] = token
    return conf_query


def gen_url(conf: dict, **kwargs):
    """
    Generates a list containing the Download URLs
    :param conf:
    :return: list
    """
    liste = []
    url = conf['API']['processing_url']
    url = url.replace('{username}', conf['Login']['username'])

    url = url.replace('{token}', conf['Login']['apitoken'])
    res = requests.get(url)
    res = json.loads(res.text.encode('utf-8'))
    api_json = res['pagination']
    total_items = api_json['items']
    pages = api_json['pages']
    #per_page = api_json['per_page']
    if kwargs:
        per_page = kwargs.get('per_page')
        url = url.replace('{per_page}', str(per_page))
    else:
        per_page = api_json['per_page']
        url = url.replace('{per_page}', str(conf['API']['scrape']['per_page']))
    for item in range(1, pages + 1):
        url_new = url
        url_new = url_new.replace('{page}', str(item))
        liste.append(url_new)

    return liste, total_items, pages, per_page


def get_collection(conf: dict, page: int):
    """
    Generates a request to extract general information about the collection
    :param page: desired page
    :param conf: configfile
    :return: json data
    """
    url = conf['API']['release_url']
    url = url.replace('{username}', conf['Login']['username'])
    res = requests.request(
        'GET',
        url,
        params=get_query(conf, page = page),
        headers=get_headers(conf),
    )
    calls_left = res.headers['X-Discogs-Ratelimit-Remaining']
    #if res.status_code == 200:
    #    data = json.loads(res.text.encode('utf-8'))

    return calls_left, res,
    #else:
        #return calls_left, res.status_code


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
    Generates a request to extract general information about the collection
    :param page:
    :param conf: configfile
    :return: json and header info
    """
    url = conf['API']['release_url']
    url = url.replace('{username}', conf['Login']['username'])
    limit = conf['API']['limit']
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
    params = get_query(configfile, page = 1)
    #for _ in range(0, 100):
     #   res = get_collection(configfile, 1)[0]
      #  print(res)
    print(gen_url(configfile))