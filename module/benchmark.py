'''
Benchmarking API Calls
'''

import module.api as api
import module.config as config
import os
import math


def benchmark_per_page(config_yaml: str):
    """
    Returns possible per_page settings for api call without exceeding api limit. Only works with collections smaller than 6000 items.

    :param config_yaml: list
    :return:
    """
    # get no of items in collection
    no = api.get_info_api(config_yaml)['pagination']['items']
    #no = 240

    # upper treshold
    upper = 100
    # lower treshold
    lower = math.ceil(no / 60)
    liste = []
    # if collection size exceeds Api Limit than return 100
    if lower >= upper:
        return [100]
        # print(f'{no} equal -> 100')
    else:
        div = upper
        handler = True
        while handler:
            mod = no % div
            res = no / div
            if 0 <= mod <= lower and res <= 100:
                res = math.ceil(res)
                if not res * 60 < no:
                    if not res > 100:
                        # print(res, mod)
                        if res not in liste:
                            liste.append(res)
            if div == lower:
                break
            div -= 1
        if not len(liste):
            liste.append(lower)

    return liste


if __name__ == '__main__':
    root_dir = os.getcwd()
    root_dir = os.path.dirname(root_dir)
    configfile = config.read_config(os.path.join(root_dir, 'config/config.yaml'))
    # print(max(cpu_count() - 1, 1))
    print(benchmark_per_page(configfile))
    # res = test(configfile)
    # print(res)
