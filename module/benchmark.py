'''
Benchmarking API Calls
'''

import module.api as api
import module.config as config
import json
import os
from multiprocessing import cpu_count
import math
import module.collection as collection

def benchmark_per_page(config_yaml: str):
    """
    Returns possible per_page settings for api call without exceeding api limit. Only works with collections smaller than 6000 items.

    :param config_yaml: list
    :return:
    """
    # get no of items in collection
    #no = api.get_info_api(config_yaml)['pagination']['items']
    no = 4534
    # if collection size exceeds Api Limit than return 100
    if no > 6000:
        return [100]
    else:

        # divider
        div = 100
        liste = []
        handler = True
        while handler:
            mod = no % div
            res = no / div
            if 0 <= mod <= 9 and res <= 100:
                res = math.ceil(res)
                if not res * 60 < no:
                    if not res > 100:
                        print(res, mod)
                        liste.append(res)
            if div == 1:
                break
            div -= 1
        if not len(liste):
            liste.append(100)
        return liste


def test (config_yaml: str):
    """
    Returns possible per_page settings for api call without exceeding api limit. Only works with collections smaller than 6000 items.

    :param config_yaml: list
    :return:
    """
    # get no of items in collection
    for no in range(6000, 1, -1):

        # if collection size exceeds Api Limit than return 100
        if no > 6000:
            return [100]
        else:

            # divider
            div = 100
            liste = []
            handler = True
            while handler:
                mod = no % div
                res = no / div
                if 0 <= mod <= 9 and res <= 100:
                    res = math.ceil(res)
                    if not res * 60 < no:
                        if not res > 100:
                            #print(res, mod)
                            liste.append(res)
                if div == 1:
                    break
                div -= 1
            if not len(liste):
                print(no)





if __name__ == '__main__':
    root_dir = os.getcwd()
    root_dir = os.path.dirname(root_dir)
    configfile = config.read_config(os.path.join(root_dir, 'config/config.yaml'))
    #print(max(cpu_count() - 1, 1))
    print(benchmark_per_page(configfile))
    #test(configfile)
