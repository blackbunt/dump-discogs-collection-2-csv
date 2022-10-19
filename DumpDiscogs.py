import sys
sys.path.append('module')
import url_checker as url_checker
import get_collection as collection
import write_to_file as writefile
import print as _print
import menu as _menu
import qr as qr
import threading
import configparser
import check_exists as exist
import urllib.request
import logging
import re

# Basic logging to file
LOG_FILENAME="debug.log"
LOG_FORMAT= "[%(levelname)s %(filename)s-%(lineno)s %(funcName)s()] %(message)s"
logger = logging.getLogger(__name__)
logging.root.handlers = []
logging.basicConfig(filename=LOG_FILENAME, format=LOG_FORMAT, level=logging.DEBUG)

# Additional logging of errors to terminal
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
formatter = logging.Formatter(LOG_FORMAT)
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

logging.debug('d e b u g')
logging.info('i n f o')
logging.warning('w a r n i n g')
logging.error('e r r o r')
logging.exception('e x p')


config = configparser.ConfigParser()
config.read('config.ini')
username = config['Login']['username']
apitoken = config['Login']['apitoken']

api_discogs = "https://api.discogs.com"

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
    print('Local webserver running on port {}\n'.format(server.server_port))

    if url_checker.url_checker(api_discogs):

        user_input = _menu.choose()

        if user_input == '0':
            fin()
            exit()

        # get collection value
        elif user_input == '1':
            print(collection.get_collection_value(username, apitoken) + "\n")

        # dump collection 2 Excel-File
        elif user_input == '2':
            _db = collection.get_collection(username, apitoken)
            qr.create_qr(_db, username, apitoken)
            writefile.write_file(_db, 'Excel')

        # dump collection 2 CSV-File
        elif user_input == '3':
            _db = collection.get_collection(username, apitoken)
            qr.create_qr(_db, username, apitoken)
            writefile.write_file(_db, 'Csv')

        # create qr codes
        elif user_input == '4':
            _db = collection.get_collection(username, apitoken)
            qr.create_qr(_db, username, apitoken)

        # dump cover art
        elif user_input == '5':
            _db = collection.get_collection(username, apitoken)
            total_items = collection.get_total_item(username, apitoken)
            exist.folder_checker('Cover-Art')
            for item in range(0, total_items + 1):
                try:
                    discogs_no = str(_db.iloc[item]['discogs_no'])
                    artist = str(_db.iloc[item]['artist'])
                    album_title = str(_db.iloc[item]['album_title'])
                    # sanitize the title (for example, album names having / in the name)
                    artist = re.sub(r'[^a-zA-Z0-9]', '_', artist)
                    album_title = re.sub(r'[^a-zA-Z0-9]', '_', album_title)

                    filename = discogs_no + "_" + artist + '-' + album_title + '.jpg'
                    cover_art_url = str(_db.iloc[item]['cover_full_url'])

                    if not exist.file_checker('Cover-Art/' + filename):
                        urllib.request.urlretrieve(cover_art_url,'Cover-Art/' + filename)
                        print("Cover for " + artist + "-" + album_title + " downloaded.")
                except:
                    None

            print("All done!\n")

    input("Press Enter to continue...\n")
