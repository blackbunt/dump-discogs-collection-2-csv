# Cleans up Artist and Title strings for Url Generartion and for .csv file

import re


def cleanup_artist(artist):  # clean up artist for entry in db
    if re.search("[(]+[\d+]+[)]+$", artist):  # removes "(digit)"
        # print("jupp " + artist_raw + " enthält (#).")
        artist = re.sub("[(]+[\d+]+[)]+$", "", artist)

    return artist


def cleanup_artist_url(artist):  # clean up artist for url-generatrion
    if re.search(" / ", artist):  # removes " / "
        # print("jupp " + artist_raw + " enthält /.")
        artist = re.sub(" / ", "-", artist)
        # print(artist_raw)

    if re.search("[(]+[\d+]+[)]+$", artist):  # removes "(digit)"
        # print("jupp " + artist_raw + " enthält (#).")
        artist = re.sub("[(]+[\d+]+[)]+$", "", artist)
        # print(artist_raw)

    if re.search("\W+[^-]", artist):  # remove unwanted chars
        # print("jupp " + artist_raw + " enthält ungewünschte zeichen.")
        artist = re.sub("\W+(?![-])", "-", artist)
        # print(artist_raw)

    if re.search("[-]+$", artist):
        # print("jupp " + artist_raw + " hat noch n Leerzeichen am Ende.")
        artist = re.sub("[-]+$", "", artist)
        # print(artist_raw)

    return artist


def cleanup_title(title):  # cleanup album-title for Url-Generation
    if re.search(" / ", title):  # removes " / "
        # print("jupp " + title_raw + " enthält /.")
        title = re.sub(" / ", "-", title)
        # print(artist_raw)

    if re.search("[(]+[\d+]+[)]+$", title):  # removes "(digit)"
        # print("jupp " + title_raw + " enthält (#).")
        title = re.sub("[(]+[\d+]+[)]+$", "", title)
        # print(title_raw)

    if re.search("\W+[^-]", title):  # remove unwanted chars
        # print("jupp " + title_raw + " enthält ungewünschte zeichen.")
        title = re.sub("\W+(?![-])", "-", title)
        # print(title_raw)

    if re.search("[-]+$", title):
        # print("jupp " + title_raw + " hat noch n Leerzeichen am Ende.")
        title = re.sub("[-]+$", "", title)
        # print(title_raw)

    return title


