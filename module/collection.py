#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dump Collection Info from Discogs API
"""
import os
import random
import time
import traceback
from functools import partial
from multiprocessing import Pool, Manager, cpu_count
from itertools import chain

import pandas as pd
import requests
from jsonpath_ng import parse
from ratelimit import limits, sleep_and_retry
from tqdm import tqdm

import config
import module.api as api
import module.setup_json as setup_json
import module.cleanup_strings as clean


@sleep_and_retry
@limits(calls=60, period=60)
def call_api(url: str):
    response = requests.get(url)

    if response.status_code == 404:
        return 'Not Found'
    if response.status_code != 200:
        pass
        #print('here', response.status_code, url)
        #raise Exception('API response: {}'.format(response.status_code))
    return response


def setup_value_data(config_yaml: dict):
    """
    Returns a list which contains all the neccesary information for 'Show Library Statistics Menu'
    :param config_yaml:
    :return: list
    """
    info = {}
    liste = []
    req = api.get_info_api(config_yaml)
    info['Username'] = config_yaml['Login']['username']
    info['Total items'] = req['pagination']['items']
    res = api.get_value_api(config_yaml)
    info['Min. Value'] = res['minimum']
    info['Med. Value'] = res['median']
    info['Max. Value'] = res['maximum']
    for key, value in info.items():
        liste.append(f'{key}: {value}')
    return liste


def setup_collection_data(config_yaml: dict):
    """
    Generate all the Urls for the Release Call.
    :param config_yaml:
    :return:
    """
    urls = api.gen_url(config_yaml)
    return urls


def get_release_data(listManager = None, links_pokemon = None, process = 0):
    #     print('Called Pokemon', process)
    link = links_pokemon[process]
    info = None
    resolved = False
    #     print(link)
    try:
        while not resolved:

            res = None
            too_many_calls = False

            try:
                res = call_api(link)
                if res == 'Not Found':
                    resolved = True
                    break
            except Exception as e:
                #print(e)
                if e == 'Too Many Requests':
                    too_many_calls = True

            if too_many_calls:
                time.sleep(60)

            elif res.status_code < 300:
                collection = []
                releases = res.json()['releases']
                # Initialize json structure
                structure, options, processing = setup_json.set_all()
                for release in releases:
                    row = {}  # for every entry in "release" a dictionary
                    # Iterate over all entries from the json setup and load the data from the server
                    for key, value in structure.items():
                        try:
                            jp = parse(value)
                            match = jp.find(release)
                            row[key] = str(match[0].value)
                        except:
                            row[key] = 'NORESULT'

                    # After loading is done, do some formatting and generations, remove _raw entries
                    for key, value in processing.items():
                        try:
                            row[key] = options[key](row[key + '_raw'])
                            row.pop(key + '_raw')
                        except:
                            traceback.print_exc()
                    # Generate URL for Webpage and QR code
                    try:
                        #row['discogs_webpage'] = gen_url(row['discogs_no'])
                        row['qr_code'] = "http://127.0.0.1:1224/qr/" \
                                         + row['discogs_no'] + "_" \
                                         + clean.cleanup_artist_url(row['artist']) + "-" \
                                         + clean.cleanup_title_url(row['album_title']) + ".png"
                    except Exception:
                        pass
                        #logger.error("", exc_info=True)

                    # add list into the dictionary "collection"
                    collection.append(row)

                resolved = True

            elif res.status_code == 429:
                #print(res.status_code)
                time.sleep(15)

            else:
                #print(res.status_code)
                sleep_val = random.randint(1, 10)
                time.sleep(sleep_val)

    except:
        pass
        #print(f'Take a short break.\n')

    finally:
        if collection != None:
            listManager.append(collection)
            #time.sleep(0.5)
            return


def get_collection_data(config_yaml: dict,):
    # cannot be 0, so max(NUMBER,1) solves this
    workers = max(cpu_count() - 1, 1)
    #workers = 1
    # create the pool
    manager = Manager()

    # Need a manager to help get the values async, the values will be updated after join
    listManager = manager.list()
    pool = Pool(workers)
    try:

        links_pokemon, total_items, pages, per_page = api.gen_url(config_yaml)
        part_get_clean_pokemon = partial(get_release_data, listManager, links_pokemon)

        #         could do this the below is visualize the rate success /etc
        #         pool.imap(part_get_clean_pokemon, list(range(0, len(links_pokemon))))
        #         using tqdm to see progress imap works
        for _ in tqdm(pool.imap(part_get_clean_pokemon, list(range(0, len(links_pokemon)))), total=len(links_pokemon),
                      desc=f'Scraping Discogs. Total items: {total_items} in blocks of {per_page}', unit='Blocks',
                      colour='yellow'):

            pass
        pool.close()
        pool.join()
    finally:
        pool.close()
        pool.join()


    collection_list = list(chain.from_iterable(listManager))



    df_collection = pd.DataFrame(collection_list)
    df_collection.sort_values(['date_added'], )
    return df_collection


if __name__ == '__main__':
    root_dir = os.getcwd()
    root_dir = os.path.dirname(root_dir)
    configfile = config.read_config(os.path.join(root_dir, 'config/config.yaml'))
    setup_json.set_json()
    setup_json.set_all()


    print(get_collection_data(configfile))
