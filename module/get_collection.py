import re
import requests
import json
import pandas as pd
import cleanup_strings as clean

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
            sep = ", "  # needed for format, styles to connect strings

            print("   Fetching item #" + str(item))
            item += 1

            try:
                artist_raw = release['basic_information']['artists'][0]['name']  # Artist
                album_title_raw = release['basic_information']['title']  # Album title
                discogs_no = str(release['basic_information']['id'])  # Discogs-ID
                year = str(release['basic_information']['year'])  # Release Year
                label = release['basic_information']['labels'][0]['name']  # Label Name
                catalog_no = str(release['basic_information']['labels'][0]['catno'])  # Catalog#
                genres = release['basic_information']['genres'][0]  # Genres
                styles = sep.join(release['basic_information']['styles'])  # Styles
                date_added = str(release['date_added'])  # Date Added
                rating = release['rating']  # Rating
                cover_low_url = release['basic_information']['thumb']  # Low-Res Cover Art Url
                cover_full_url = release['basic_information']['cover_image']  # Full-Res Cover Art Url

                row['discogs_no'] = discogs_no
                row['artist_raw'] = artist_raw
                row['album_title'] = album_title_raw
                row['year'] = year
                row['label'] = label
                row['catalog#'] = catalog_no
                row['genres'] = genres
                row['styles'] = styles
                row['date_added'] = date_added
                row['rating'] = rating
                row['cover_low_url'] = cover_low_url
                row['cover_full_url'] = cover_full_url

            except:
                print("   EXCEPTION: JSON logic changed. - item #" + str(item - 1) + " - "
                      + str(release['basic_information']['title']))

            try:
                media_condition = release['notes'][0]['value']  # Media Condition
                sleeve_condition = release['notes'][1]['value']  # Sleeve Condition
                row['media_condition'] = media_condition
                row['sleeve_condition'] = sleeve_condition

            except:
                media_condition = sleeve_condition = "no condition"
                row['media_condition'] = media_condition
                row['sleeve_condition'] = sleeve_condition

            try:
                format = sep.join(release['basic_information']['formats'][0]['descriptions'])  # Format
                discogs_webpage = gen_url(clean.cleanup_artist_url(artist_raw),
                                          clean.cleanup_title(album_title_raw),
                                          discogs_no)
                artist = clean.cleanup_artist(artist_raw)  # removes ( digit )
                qr_code = "http://127.0.0.1:1224/qr/" + discogs_no + "_" + artist.replace(" ", "%20").replace("?", "3F") \
                          + "-" + \
                          album_title_raw.replace(" ", "%20").replace("?", "3F") \
                          + ".png"

                row['format'] = format
                row['discogs_webpage'] = discogs_webpage
                row['artist'] = artist
                row['qr_code'] = qr_code

            except:
                print("   WARNING: Formatting & QR code - item #" + str(item - 1) + " - "
                      + str(release['basic_information']['title']))

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
