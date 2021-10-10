import re
import requests
import json
import pandas as pd
import cleanup_strings as clean
from jsonpath_ng import parse
import setup_json
import traceback

API_BASEURL = "https://api.discogs.com"
API_FORMAT = "application/vnd.discogs.v2.plaintext+json"
API_LIMIT = 100
CONVERTION_RATIO = 20
DATA_FILE = '../db.csv'
HTTPS_BASEURL = "https://www.discogs.com/"

debug_mode = False

def gen_url(discogs_no):

    # Generate Discogs-Url
    discogs_url = HTTPS_BASEURL + "release/" + discogs_no
    print(discogs_url)
    return discogs_url

def get_headers():
    return {
        'Accept': API_FORMAT,
        'Content-Type': 'application/json',
        'User-Agent': 'discogs2csv'}

def get_query(apikey):
    return {
        'token': apikey,
        'per_page': API_LIMIT,
        'page': 1}


def get_total_item(username, apikey):
    headers = get_headers()
    query = get_query(apikey)

    # get json from API
    session = requests.session()
    r = session.get(API_BASEURL + '/users/' + username + '/collection/folders/0/releases', params=query,
                    headers=headers)
    jsondoc = json.loads(r.text.encode('utf-8'))
    total_items = int(jsondoc['pagination']['items'])
    return total_items


def get_collection(username, apikey):
    headers = get_headers()
    query = get_query(apikey)

    collection = []  # creates empty list for collection

    # get json from API
    session = requests.session()
    r = session.get(API_BASEURL + '/users/' + username + '/collection/folders/0/releases', params=query,
                    headers=headers)
    jsondoc = json.loads(r.text.encode('utf-8'))

    if "message" in jsondoc:
        print("** Message from server: '{}' **".format(jsondoc["message"]))

    total_pages = int(jsondoc['pagination']['pages'])
    total_items = int(jsondoc['pagination']['items'])
    item = 1
    print("\nDumping Collection. This can take some time...\n")
    print("Total items in Collection: {}\n".format(total_items))

    # Initialize json structure
    structure, options, processing = setup_json.set_all()

    # for every release in (all) releases create a dictionary and store it in a list
    for page in range(1, total_pages + 1):
        print("Fetching Page {} of {}.".format(page, total_pages))

        query = {
            'token': apikey,
            'per_page': API_LIMIT,
            'page': page}

        r = session.get(API_BASEURL + '/users/' + username + '/collection/folders/0/releases', params=query,
                        headers=headers)

        releases = r.json()['releases']

        for release in releases:
            row = {}  # for every entry in "release" a dictionary

            print("   Fetching item # {}".format(item))
            item += 1

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
                row['discogs_webpage'] = gen_url(row['discogs_no'])
                row['qr_code'] = "http://127.0.0.1:1224/qr/" \
                    + row['discogs_no'] + "_" \
                    + clean.cleanup_artist_url(row['artist']) + "-" \
                    + clean.cleanup_title_url(row['album_title']) + ".png"
            except Exception:
                traceback.print_exc()

            # add list into the dictionary "collection"
            collection.append(row)
            if (item >= 2) & debug_mode:
                break

        if (item >= 2) & debug_mode:
            break



    print("Collection created!")

    # create pandas data frame
    df = pd.DataFrame(collection)
    return df


def get_collection_value(username, apikey):
    value = []  # create empty dictionary
    row = {}

    headers = get_headers()
    query = get_query(apikey)

    # get json from API
    session = requests.session()
    v = session.get(API_BASEURL + '/users/' + username + '/collection/value', params=query, headers=headers)
    row['minimum'] = v.json()['minimum']
    row['median'] = v.json()['median']
    row['maximum'] = v.json()['maximum']

    # merge list in dictionary
    value.append(row)

    # create pandas data frame
    df = pd.DataFrame(value)

    return df
