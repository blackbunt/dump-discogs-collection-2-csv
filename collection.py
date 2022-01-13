#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dump Collection Info from Discogs API multithreaded
"""
import os
import platform
import sys
import random
import time
import traceback
import signal
import requests
import multiprocessing
from functools import partial
from multiprocessing import Pool, Manager, cpu_count
from multiprocessing.managers import SyncManager
from itertools import chain
from keyboard import wait
from pick import pick
from jsonpath_ng import parse
from ratelimit import limits, sleep_and_retry
from tqdm import tqdm

import pandas as pd

import module.api as api
import module.setup_json as setup_json
import module.cleanup_strings as clean
import module.benchmark as benchmark
import module.login as login
import module.config as config
import module.write_to_file as write_to_file


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
    """
    Calls API, handles response and returns formatted data of response as a pandas dataframe
    :param list_manager:
    :param links_discogs: link to call
    :param process:
    :return: response from call as a pandas dataframe
    """
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


def mgr_init():
    """
    initializer for SyncManager
    :return: Nating sasa ke
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def get_collection_data(config_yaml: dict, **kwargs):
    """
    Handles the call of get_release_data, Multiprocessing
    :param config_yaml: config from yaml
    :param kwargs:
    per_page: set custom value per_page: int for url request
    :return: pandas dataframe with the whole collection, total needed time: float
    """
    # cannot be 0, so max(NUMBER,1) solves this
    workers = max(cpu_count() - 1, 1)
    # workers = 4
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
    """
    Runs Benchmark against the Discogs Api to find the best suited settings for the config
    :param config_yaml: config yaml
    :return: optimal value for per_page: int
    """
    res_dict = {}
    res = benchmark.benchmark_per_page(config_yaml)
    print(res)
    print('wait for api time reset')
    time.sleep(60)

    togo = len(res)
    time_left = len(res) * 60
    for entry in res:
        elapsed = get_collection_data(config_yaml, per_page=entry)[1]
        res_dict[entry] = elapsed
        togo -= togo
        time_left = time_left - 60
        print(f'just ca. {time_left / 60} minutes to go!')
        print(entry, elapsed)
        print(' wait a minute...')

        time.sleep(61)
    min_val = min(res_dict.items(), key=lambda x: x[1])
    # print(dict)
    # print(min_val)
    print(f'Optimal settings:\nper page: {min_val[0]}\nest. time: {min_val[1]} sec.')
    return int(min_val[0])


def clear_scr():
    """
    Clears output screen
    :return: None
    """
    system = platform.system()
    if system == 'Windows':
        clear = lambda: os.system('cls')
        clear
    elif system == 'Linux' or platform == 'Darwin':
        clear = lambda: os.system('clear')
        clear()
    else:
        pass
    return None


def not_implemented_yet():
    """
    Placeholder func
    :return: Nada
    """
    print('Not implemented yet. Continue with >Enter<')
    wait('Enter')


def show_menu(configuration: dict, def_index=0, def_back=False, **kwargs):
    """
    Renders a simple menu from input config
    :param def_back: inserts a "Back to Menu option into the list at top, default is disabled
    :param def_index: position of indicator position, default value == 0
    :param configuration: a dict including a key title (str) and a key options (list)
    **kwargs:
    'title' change title if Config is empty
    :return: list: option, index
    Returns a list with the chosen option and the index number of the input 'options' list
    """
    if 'options' in configuration and 'title' in configuration:
        options = configuration['options']
        # add Back to Main Menu Option
        if def_back:
            if options[0] != 'Back to Main Menu':
                options.insert(0, 'Back to Main Menu')
        title = configuration['title']
        # if title value in menu.yaml is None than use kwargs
        if title is None:
            title = kwargs.get('title')
        option, index = pick(options, title, indicator='•', default_index=def_index)
    else:
        raise TypeError("Missing key 'title' or missing key 'options'.")

    return [option, index]


def menu_yes_no(message: str):
    """
    Renders a yes/no option menu, returns choice
    :param message: message printed for decision
    :return:
    """
    conf = {
        'title': message,
        'options': [
            'Yes',
            'No'
        ]
    }
    res = show_menu(conf, 1, title=message)
    return res


def menu_login_data(menu_config_yaml: dict, gen_config_yaml: dict, gen_config_path: str):
    """
    Renders the Configure Login Data Menu and execute the chosen options.
    :param gen_config_path: str containing the path to config.yaml
    :param gen_config_yaml: config from the config.yaml
    :param menu_config_yaml: config from the menu.yaml key LoginData
    :return:
    """
    conf = menu_config_yaml['LoginData']
    res = show_menu(conf, 0, True)
    username = gen_config_yaml['Login']['username']
    apitoken = gen_config_yaml['Login']['apitoken']
    if res[1] == 0:  # Back to Main Menu
        menu_main(menu_config_yaml, gen_config_yaml, gen_config_path)
    elif res[1] == 1:  # change username
        res = login.chg_username(gen_config_path, username, True)
        # if nothing changed run menu_login_data again
        if res == 1:
            menu_login_data(menu_config_yaml, gen_config_yaml, gen_config_path)
        else:
            pass
    elif res[1] == 2:  # change apitoken
        res = login.chg_apitoken(gen_config_path, apitoken, True)
        # if nothing changed run menu_login_data again
        if res == 1:
            menu_login_data(menu_config_yaml, gen_config_yaml, gen_config_path)
        else:
            pass
    else:
        raise RuntimeError('Should not be able to be here!')


def menu_main(menu_config_yaml: dict, gen_config_yaml: dict, gen_config_path):
    """
    Renders the main menu and execute the chosen options.
    :param gen_config_path:
    :param gen_config_yaml: config from the config.yaml
    :param menu_config_yaml: config from the menu.yaml key MainMenu
    :return: Nothing (Yet)
    """
    config_file = menu_config_yaml['MainMenu']
    res = show_menu(config_file, 0)
    if res[1] == 0:  # Run Data Dump 2 Excel File
        setup_json.set_json()
        setup_json.set_all()
        clear_scr()
        data, est_time = get_collection_data(gen_config_yaml)
        write_to_file.write_file(data, 'Excel')
        menu_main(menu_config_yaml, gen_config_yaml, gen_config_path)
    elif res[1] == 1:  # Run Data Dump 2 CSV File
        setup_json.set_json()
        setup_json.set_all()
        clear_scr()
        data, est_time = get_collection_data(gen_config_yaml)
        write_to_file.write_file(data, 'Csv')
        menu_main(menu_config_yaml, gen_config_yaml, gen_config_path)
    elif res[1] == 2:  # Run Show Library Statistics
        menu_statistics(menu_config_yaml, gen_config_yaml, gen_config_path)
    elif res[1] == 3:  # Configure Login Data
        menu_login_data(menu_config_yaml, gen_config_yaml, gen_config_path)
    elif res[1] == 4:  # Exit Program
        sys.exit()
    else:
        sys.exit()


def menu_statistics(menu_config_yaml: dict, gen_config_yaml: dict, gen_config_path):
    """
    Renders the statistics menu and the statistics data.
    :param gen_config_path:
    :param gen_config_yaml: config from the config.yaml
    :param menu_config_yaml: config from the menu.yaml key MainMenu
    :return: Nothing (Yet)
    """

    text = setup_value_data(gen_config_yaml)
    title = ''
    for index in range(0, len(text)):
        title = title + f'{text[index]}\n'
    conf = {
        'title': 'Show Library Statistics\n\n' + title,
        'options': ['Back to Main Menu']
    }
    res = show_menu(conf, 0, True)
    if res[1] == 0:
        menu_main(menu_config_yaml, gen_config_yaml, gen_config_path)
    else:
        raise RuntimeError


if __name__ == '__main__':
    multiprocessing.freeze_support()
    # root_dir = os.getcwd()
    # root_dir = os.path.dirname(root_dir)
    # configfile = config.read_config(os.path.join(root_dir, 'config/config.yaml'))
    # setup_json.set_json()
    # setup_json.set_all()

    # res, elapsed = get_collection_data(configfile)
    # print(elapsed)
    # import module.write_to_file as write_to_file

    # write_to_file.write_file(res, 'Excel')

    # benchmark
    # dict = {4: 22.18367600440979, 5: 11.012670040130615, 6: 37.60151791572571, 8: 13.83693814277649, 10: 6.8414952754974365, 12: 10.590538740158081, 15: 5.543498754501343, 16: 6.0455851554870605, 18: 7.157623291015625, 20: 5.590988636016846, 24: 4.8190929889678955, 30: 6.920377254486084, 35: 6.198363304138184, 40: 7.531091213226318, 48: 8.57279372215271, 60: 9.31027603149414}
    # run_benchmark(configfile)
    root_dir = os.getcwd()
    # must be commented out to work in pycharm debugger
    #root_dir = os.path.dirname(root_dir)
    CONFIG_PATH = os.path.join(root_dir, 'config/config.yaml')
    MENU_PATH = os.path.join(root_dir, 'config/menu.yaml')
    # clear output window
    # menu.clear_scr()
    # load general config files
    # global gen_config
    gen_config = config.read_config(CONFIG_PATH)
    # load menu config file
    menu_config = config.read_config(MENU_PATH)

    # check if login data exists/connection is possible
    if not login.check_login(gen_config, CONFIG_PATH):
        sys.exit('Connection to Discogs not possible.\nNo Network Connection?')
    menu_main(menu_config, gen_config, CONFIG_PATH)
    #get_collection_data(gen_config)