from qrcode import *
import qrcode.image.pil

import check_exists as exist


def gen_qr(discogs_link, discogs_no, artist, album_title):
    exist.folder_checker("qr")


    # output filename
    filename = discogs_no + "_" + artist + "-" + album_title + ".png"
    if not exist.file_checker(filename):
        # Create qr code instance
        qr = QRCode(version=4, box_size=5, border=0, error_correction=ERROR_CORRECT_L)
        qr.add_data(discogs_link)
        qr.make()

        qr.make(fit=True)
        im = qr.make_image(qrcode.image.pil.PilImage)
        im.save("qr/" + filename)

