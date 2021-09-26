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


def gen_url(artist, album_title, discogs_no):
    base_url = "https://www.discogs.com/"

    artist_url = clean.cleanup_artist(artist)
    title_url = clean.cleanup_title(album_title)

    # Generate Discogs-Url
    discogs_url = base_url + artist_url + "-" + title_url + "/release/" + discogs_no
    return discogs_url


def get_total_item(username, apikey):
    # Header for API-Call
    headers = {
        'Accept': API_FORMAT,
        'Content-Type': 'application/json',
        'User-Agent': 'discogs2csv'}
    query = {
        'token': apikey,
        'per_page': API_LIMIT,
        'page': 1}

    collection = []  # creates empty list for collection

    # get json from API
    session = requests.session()
    r = session.get(API_BASEURL + '/users/' + username + '/collection/folders/0/releases', params=query,
                    headers=headers)
    jsondoc = json.loads(r.text.encode('utf-8'))
    total_items = int(jsondoc['pagination']['items'])
    return total_items


def get_collection(username, apikey):
    # Header for API-Call
    headers = {
        'Accept': API_FORMAT,
        'Content-Type': 'application/json',
        'User-Agent': 'discogs2csv'}
    query = {
        'token': apikey,
        'per_page': API_LIMIT,
        'page': 1}

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
    print("")
    print("Dumping Collection. This can take some time...")
    print("Total items in Collection: " + str(total_items))
    print("")

    # Initialize json structure
    structure, options, processing = setup_json.set_all()

    # for every release in (all) releases create a dictionary and store it in a list
    for page in range(1, total_pages + 1):
        print("Fetching Page " + str(page) + " of " + str(total_pages))

        query = {
            'token': apikey,
            'per_page': API_LIMIT,
            'page': page}

        r = session.get(API_BASEURL + '/users/' + username + '/collection/folders/0/releases', params=query,
                        headers=headers)

        releases = r.json()['releases']

        for release in releases:
            row = {}  # for every entry in "release" a dictionary

            print("   Fetching item #" + str(item))
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
                row['discogs_webpage'] = gen_url(row['artist'],row['album_title'],row['discogs_no'])
                row['qr_code'] = "http://127.0.0.1:1224/qr/" + row['discogs_no'] + "_" + row['artist']\
                     .replace(" ", "%20").replace("?", "3F") + "-" + clean.cleanup_title(row['album_title']) + ".png"
            except Exception:
                traceback.print_exc()

            # add list into the dictionary "collection"
            collection.append(row)

    print("Success!")

    # create pandas data frame
    df = pd.DataFrame(collection)
    return df


def get_collection_value(username, apikey):
    value = []  # create empty dictionary
    row = {}

    # Header for API-Call
    headers = {
        'Accept': API_FORMAT,
        'Content-Type': 'application/json',
        'User-Agent': 'discogs2csv'}
    query = {
        'token': apikey,
        'per_page': API_LIMIT,
        'page': 1}

    # get json from API
    session = requests.session()
    v = session.get(API_BASEURL + '/users/' + username + '/collection/value', params=query, headers=headers)
    value_min = v.json()['minimum']
    value_med = v.json()['median']
    value_max = v.json()['maximum']

    # create list with following values
    row['minimum'] = value_min
    row['median'] = value_med
    row['maximum'] = value_max

    # merge list in dictionary
    value.append(row)

    # create pandas data frame
    df = pd.DataFrame(value)

    return df
