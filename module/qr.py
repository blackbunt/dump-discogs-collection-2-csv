from qrcode import *
import qrcode.image.pil

import check_exists as exist
import cleanup_strings as clean
import get_collection as collection
import traceback


def create_qr(_db, username, apitoken):
    total_items = collection.get_total_item(username, apitoken)
    print("Going to create {} QR codes:\n".format(total_items))
    for item in range(0, total_items):
        try:
            discogs_no = str(_db.iloc[item]['discogs_no'])
            artist = str(_db.iloc[item]['artist'])
            album_title = str(_db.iloc[item]['album_title'])
            discogs_link = str(_db.iloc[item]['discogs_webpage'])
            gen_qr(discogs_link, discogs_no, artist, album_title, item)
        except Exception:
            print("Unable to create QR code for json-array # {} with album {}".format(item, album_title))
            traceback.print_exc()

    print("All done!\n")


def gen_qr(discogs_link, discogs_no, artist, album_title, item='None'):
    exist.folder_checker("qr")


    # output filename
    filename = discogs_no + "_" + clean.cleanup_artist_url(artist) + "-" + clean.cleanup_title_url(album_title) + ".png"
    if not exist.file_checker(filename):
        # Create qr code instance
        qr = QRCode(version=4, box_size=5, border=0, error_correction=ERROR_CORRECT_L)
        qr.add_data(discogs_link)
        qr.make()

        qr.make(fit=True)
        im = qr.make_image(qrcode.image.pil.PilImage)
        im.save("qr/" + filename)

    print("Created QR code # {} for '{}-{}'.".format(item+1, artist, album_title))

