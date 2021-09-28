# Cleans up Artist and Title strings for Url Generartion and for .csv file

import re


def cleanup_artist(artist):  # removes "( digit )"
    print("cleanup_artist: " + artist)
    if re.search("[(]+[\d+]+[)]+$", artist):  # removes "(digit)"
        artist = re.sub("[(]+[\d+]+[)]+$", "", artist)
    artist = artist.rstrip()
    print("nach strip:**" + artist + "*****")
    return artist


def cleanup_artist_url(artist):  # url-generatrion

    artist = cleanup_artist(artist)

    print("cleanup_artist_url:" + artist)

    if re.search(" / ", artist):  # removes " / "
        artist = re.sub(" / ", "-", artist)

    if re.search("\W+[^-]", artist):  # remove unwanted chars
        artist = re.sub("\W+(?![-])", "-", artist)

    if re.search("[-]+$", artist):
        artist = re.sub("[-]+$", "", artist)

    if re.search("/", artist):
        artist = re.sub("/","-", artist)

    print("artist_url:" + artist)
    return artist


def cleanup_title(title):

    if re.search(" + ", title):  # removes " / "
        title = re.sub(" / ", "-", title)

    if re.search("[(]+[\d+]+[)]+$", title):  # removes "(digit)"
        title = re.sub("[(]+[\d+]+[)]+$", "", title)

    if re.search("\W+[^-]", title):  # remove unwanted chars
        title = re.sub("\W+(?![-])", "-", title)

    if re.search("[-]+$", title):
        title = re.sub("[-]+$", "", title)

    if re.search("/", title):
        title = re.sub("/", "-", title)

    return title

def cleanup_title_url(title):

    title = cleanup_title(title)

    print("cleanup_title: " + title)
    
    if re.search(" + ", title):  # removes " / "
        title = re.sub(" / ", "-", title)

    if re.search("[(]+[\d+]+[)]+$", title):  # removes "(digit)"
        title = re.sub("[(]+[\d+]+[)]+$", "", title)

    if re.search("\W+[^-]", title):  # remove unwanted chars
        title = re.sub("\W+(?![-])", "-", title)

    if re.search("[-]+$", title):
        title = re.sub("[-]+$", "", title)

    if re.search("/", title):
        title = re.sub("/", "-", title)

    if re.search(" ", title):
        title = re.sub(" ", "-", title)

    print("title: " + title)
        
    return title

def cleanup_styles(styles):
    return styles.replace("[","").replace("]","").replace("'","")

