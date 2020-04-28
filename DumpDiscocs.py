import sys
sys.path.append('module')
import url_checker as url_checker
import get_collection as collection
import cleanup_strings as clean
import write_to_file as writefile
import print as _print
import menu as _menu
import qr as qr
import threading
import configparser
import check_exists as exist
import urllib.request


config = configparser.ConfigParser()
config.read('config.ini')
username = config['Login']['username']
apitoken = config['Login']['apitoken']


try:
    from http.server import HTTPServer, SimpleHTTPRequestHandler  # Python 3
except ImportError:
    from SimpleHTTPServer import BaseHTTPServer

    HTTPServer = BaseHTTPServer.HTTPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler  # Python 2

server = HTTPServer(('localhost', 1224), SimpleHTTPRequestHandler)
thread = threading.Thread(target=server.serve_forever)
thread.daemon = True
thread.start()


def fin():
    server.shutdown()

while True:
    _print.title()
    print('server running on port {}'.format(server.server_port))
    user_input = _menu.choose()

    if user_input == '0':
        fin()
        exit()

    # get collection value
    elif user_input == '1':
        if url_checker.url_checker("https://api.discogs.com"):
            print("Connection to Discogs established.")
            print("")
            _db_val = collection.get_collection_value(username, apitoken)
            print(_db_val)
            input("Press Enter to continue...")

        else:
            print("No Connection to Discogs possible...")
            input("Press Enter to continue...")

    # dump collection 2 Excel-File
    elif user_input == '2':
        if url_checker.url_checker("https://api.discogs.com"):
            print("Connection to Discogs established.")
            print("")
            _db = collection.get_collection(username, apitoken)

            while True:
                filename = str(input("Enter Filename of Excel-File: "))
                if filename != "_db":
                    writefile.write_2_excel(_db, filename)
                    print("Write to File successful.")
                    input("Press Enter to continue...")
                    break;

                else:
                    print("You can't name the file '_db' !")
                    input("Press Enter to continue...")

        else:
            print("No Connection to Discogs possible...")
            input("Press Enter to continue...")

    # dump collection 2 Excel-File
    elif user_input == '3':
        if url_checker.url_checker("https://api.discogs.com"):
            print("Connection to Discogs established.")
            print("")
            _db = collection.get_collection(username, apitoken)

            while True:
                filename = str(input("Enter Filename of Csv-File: "))
                if filename != "_db":
                    writefile.write_2_csv(_db, filename)
                    print("Write to File successful.")
                    input("Press Enter to continue...")

                else:
                    print("You can't name the file '_db' !")
                    input("Press Enter to continue...")

        else:
            print("No Connection to Discogs possible...")
            input("Press Enter to continue...")

    # create qr codes
    elif user_input == '4':
        if url_checker.url_checker("https://api.discogs.com"):
            print("Connection to Discogs established.")
            print("")

            _db = collection.get_collection(username, apitoken)
            total_items = collection.get_total_item(username, apitoken)

            for item in range(0, total_items + 1):
                try:
                    discogs_no = str(_db.iloc[item]['discogs_no'])
                    artist = str(_db.iloc[item]['artist'])
                    album_title = str(_db.iloc[item]['album_title'])
                    discogs_link = str(_db.iloc[item]['discogs_webpage'])
                    qr.gen_qr(discogs_link, discogs_no, artist, album_title)
                    print("QR-Code for " + artist + "-" + album_title + " created.")
                except:
                    None
            print("All done!")
            input("Press Enter to continue...")

    # dump cover art
    elif user_input == '5':
        if url_checker.url_checker("https://api.discogs.com"):
            print("Connection to Discogs established.")
            print("")
            _db = collection.get_collection(username, apitoken)
            total_items = collection.get_total_item(username, apitoken)
            exist.folder_checker('Cover-Art')
            for item in range(0, total_items + 1):
                try:
                    discogs_no = str(_db.iloc[item]['discogs_no'])
                    artist = str(_db.iloc[item]['artist'])
                    album_title = str(_db.iloc[item]['album_title'])

                    filename = discogs_no + "_" + artist + '-' + album_title + '.jpg'
                    cover_art_url = str(_db.iloc[item]['cover_full_url'])

                    if not exist.file_checker('Cover-Art/' + filename):
                        urllib.request.urlretrieve(cover_art_url,'Cover-Art/' + filename)
                        print("Cover for " + artist + "-" + album_title + " downloaded.")
                except:
                    None

            print("All done!")
            input("Press Enter to continue...")
