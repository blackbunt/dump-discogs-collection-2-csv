import json
import requests
import csv



username = "your_username"
apikey = "your_api_key"

API_BASEURL = "https://api.discogs.com"
API_FORMAT = "application/vnd.discogs.v2.plaintext+json"
API_LIMIT = 100
CONVERTION_RATIO = 20
DATA_FILE = 'db.csv'

print("Fetching data from Discogs...")

headers = {
    'Accept': API_FORMAT,
    'Content-Type': 'application/json',
    'User-Agent': 'discogs2csv'}
query = {
    'token': apikey,
    'per_page': API_LIMIT,
    'page': 1}

session = requests.session()
r = session.get(API_BASEURL + '/users/' + username + '/collection/folders/0/releases', params=query, headers=headers)
jsondoc = json.loads(r.text.encode('utf-8'))
total_pages = int(jsondoc['pagination']['pages'])

v = session.get(API_BASEURL + '/users/' + username + '/collection/value', params=query, headers=headers)
value_min = v.json()['minimum']
value_med = v.json()['median']
value_max = v.json()['maximum']



with open(DATA_FILE, 'w', newline='') as f:
    writer = csv.writer(f, delimiter=',', dialect='excel')
    #writer.writerow([""username"", "Discogs Collection Dump", "Value:", "Minimum: " + value_min])
    #writer.writerow(["", "", "", "Median: " + value_med])
    #writer.writerow(["", "", "",  "Maximum: " + value_max])
    #writer.writerow([])
    writer.writerow(["Discogs-Id", "Artist", "Album Title", "Year", "Format", "Media-Condition", "Sleeve-Condition",
                     "Label", "Catalog#", "Genres", "Styles", "Date added", "Rating",
                     "Cover Low Url", "Cover Full Url"])

    for page in range(1, total_pages + 1):
        print("Fetching Page " + str(page) + " of " + str(total_pages))
        query = {
            'token': apikey,
            'per_page': API_LIMIT,
            'page': page}
        r = session.get(API_BASEURL + '/users/' + username + '/collection/folders/0/releases', params=query,
                        headers=headers)
        data = r.json()
        releases = r.json()['releases']

        for sample in releases:
            sep = ", "  # for joining strings
            try:
                artist = sample['basic_information']['artists'][0]['name']                      # Artist
                album_title = sample['basic_information']['title']                              # Album title
                year = str(sample['basic_information']['year'])                                 # Release Year
                cover_full = sample['basic_information']['cover_image']                         # Full-Res Cover Art Url
                cover_low = sample['basic_information']['thumb']                                # Low-Res Cover Art Url
                genres = sample['basic_information']['genres'][0]                               # Genres
                styles = sep.join(sample['basic_information']['styles'])                        # Styles
                id = str(sample['basic_information']['id'])                                     # Discogs-ID
                format = sep.join(sample['basic_information']['formats'][0]['descriptions'])    # Format
                label_name = sample['basic_information']['labels'][0]['name']                   # Label Name
                catno = str(sample['basic_information']['labels'][0]['catno'])                  # Catalog#
                added = str(sample['date_added'])                                               # Date Added
                cond_media = sample['notes'][0]['value']                                        # Media Condition
                cond_sleeve = sample['notes'][1]['value']                                       # Sleeve Condition
                rating = sample['rating']                                                       # Rating
            except:
                None


            writer.writerow([id, artist, album_title, year, format, cond_media, cond_sleeve, label_name, catno,
                             genres, styles, added, rating, cover_low, cover_full + ","])
    f.close()
print("All saved to csv!")
