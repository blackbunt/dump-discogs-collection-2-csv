#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dump Collection Info from Discogs API multithreaded
"""
import os
import random
import time
import traceback
import signal
from functools import partial
from multiprocessing import Pool, Manager, cpu_count
from multiprocessing.managers import SyncManager
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
import module.benchmark as benchmark


@sleep_and_retry
@limits(calls=60, period=60)
def call_api(url: str):
    response = requests.get(url)

    if response.status_code == 404:
        return 'Not Found'
    if response.status_code != 200:
        pass
        # print('here', response.status_code, url)
        # raise Exception('API response: {}'.format(response.status_code))
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


def get_release_data(list_manager=None, links_discogs=None, process=0):
    # https://hackernoon.com/multiprocessing-for-heavy-api-requests-with-python-and-the-pokeapi-3u4h3ypn
    # scrapes api multiprocessed. return pd df and a float with the total elapsed time.
    link = links_discogs[process]
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
                # print(e)
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
                        # row['discogs_webpage'] = gen_url(row['discogs_no'])
                        row['qr_code'] = "http://127.0.0.1:1224/qr/" \
                                         + row['discogs_no'] + "_" \
                                         + clean.cleanup_artist_url(row['artist']) + "-" \
                                         + clean.cleanup_title_url(row['album_title']) + ".png"
                    except Exception:
                        pass
                        # logger.error("", exc_info=True)

                    # add list into the dictionary "collection"
                    collection.append(row)

                resolved = True

            elif res.status_code == 429:
                # print(res.status_code)
                time.sleep(15)

            else:
                # print(res.status_code)
                sleep_val = random.randint(1, 10)
                time.sleep(sleep_val)

    except:
        pass
        # print(f'Take a short break.\n')

    finally:
        if collection != None:
            list_manager.append(collection)
            # time.sleep(0.5)
            return


# initializer for SyncManager
def mgr_init():
    signal.signal(signal.SIGINT, signal.SIG_IGN)




def get_collection_data(config_yaml: dict, **kwargs):
    # cannot be 0, so max(NUMBER,1) solves this
    workers = max(cpu_count() - 1, 1)
    #workers = 4
    # create the pool
    manager = SyncManager()
    manager.start(mgr_init)
    # Need a manager to help get the values async, the values will be updated after join
    list_manager = manager.list()
    pool = Pool(workers)
    try:
        # for benchmark
        if kwargs:
            p_page = kwargs.get('per_page')
            links_discogs, total_items, pages, per_page = api.gen_url(config_yaml, per_page=p_page)
        # for normal use
        else:
            links_discogs, total_items, pages, per_page = api.gen_url(config_yaml)
        part_get_clean_release = partial(get_release_data, list_manager, links_discogs)

        #         could do this the below is visualize the rate success /etc
        #         pool.imap(part_get_clean_release, list(range(0, len(links_discogs))))
        #         using tqdm to see progress imap works
        # build progressbar and thread for every url in the list manager
        t = tqdm(pool.imap(part_get_clean_release, list(range(0, len(links_discogs)))), total=len(links_discogs),
                 desc=f'Scraping Discogs. Total items: {total_items} in blocks of {per_page}', unit='Blocks',
                 colour='yellow')
        for _ in t:
            # return the elapsed time for scraping
            elapsed = t.format_dict["elapsed"]
            pass
        pool.close()
        pool.join()
    finally:
        pool.close()
        pool.join()



    # remove unnecessary nestings in list
    collection_list = list(chain.from_iterable(list_manager))
    df_collection = pd.DataFrame(collection_list)
    df_collection.sort_values(["date_added", "artist"], axis=0, ascending=[False, True], inplace=True)
    # df_collection.sort_values(['date_added'], )
    manager.shutdown()
    return df_collection, elapsed

def run_benchmark(config_yaml: str):
    dict = {}
    res = benchmark.benchmark_per_page(configfile)
    print(res)
    print('wait for api time reset')
    time.sleep(60)

    togo = len(res)
    time_left = len(res) * 60
    for entry in res:
        elapsed = get_collection_data(configfile, per_page=entry)[1]
        dict[entry] = elapsed
        togo -= togo
        time_left = time_left - 60
        print(f'just ca. {time_left / 60} minutes to go!')
        print(entry, elapsed)
        print(' wait a minute...')

        time.sleep(61)
    min_val = min(dict.items(), key=lambda x: x[1])
    #print(dict)
    #print(min_val)
    print(f'Optimal settings:\nper page: {min_val[0]}\nest. time: {min_val[1]} sec.')
    return min_val[0]


if __name__ == '__main__':
    root_dir = os.getcwd()
    root_dir = os.path.dirname(root_dir)
    configfile = config.read_config(os.path.join(root_dir, 'config/config.yaml'))
    #setup_json.set_json()
    #setup_json.set_all()

    #res, elapsed = get_collection_data(configfile)
    #print(elapsed)
    #import module.write_to_file as write_to_file

    #write_to_file.write_file(res, 'Excel')

    # benchmark
    #dict = {4: 22.18367600440979, 5: 11.012670040130615, 6: 37.60151791572571, 8: 13.83693814277649, 10: 6.8414952754974365, 12: 10.590538740158081, 15: 5.543498754501343, 16: 6.0455851554870605, 18: 7.157623291015625, 20: 5.590988636016846, 24: 4.8190929889678955, 30: 6.920377254486084, 35: 6.198363304138184, 40: 7.531091213226318, 48: 8.57279372215271, 60: 9.31027603149414}
    run_benchmark(configfile)