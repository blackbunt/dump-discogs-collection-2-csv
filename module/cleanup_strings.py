# Cleans up Artist and Title strings for Url Generartion and for .csv file

import re

DEBUG = False

def cleanup_artist(artist):  # removes "( digit )"
    artist = re.sub("[(]+[\d+]+[)]+$", "", artist)
    artist = artist.rstrip()
    return artist


def cleanup_artist_url(artist):  # url-generatrion

    artist = cleanup_artist(artist)

    artist = re.sub(" / ", "-", artist)

    artist = re.sub("\W+(?![^-])", "-", artist)

    artist = re.sub("[-]+$", "", artist)

    artist = re.sub("/","-", artist)

    artist = re.sub(" ", "-", artist)

    if DEBUG: print("artist_url:" + artist)
    return artist


def cleanup_title(title):

    title = re.sub(" / ", "-", title)

    title = re.sub("[(]+[\d+]+[)]+$", "", title)

    title = re.sub("\W+(?![^-])", "-", title)

    title = re.sub("[-]+$", "", title)

    title = re.sub("/", "-", title)

    if DEBUG: print("title: " + title)
    return title

def cleanup_title_url(title):

    title = cleanup_title(title)

    if DEBUG: print("cleanup_title: " + title)
    
    title = re.sub(" / ", "-", title)

    title = re.sub("[(]+[\d+]+[)]+$", "", title)

    if re.search("\W+[^-]", title):  # remove unwanted chars
        title = re.sub("\W+(?![-])", "-", title)

    if re.search("[-]+$", title):
        title = re.sub("[-]+$", "", title)

    if re.search("/", title):
        title = re.sub("/", "-", title)

    if re.search(" ", title):
        title = re.sub(" ", "-", title)

    if DEBUG: print("title: " + title)
        
    return title

def cleanup_styles(styles):
    return styles.replace("[","").replace("]","").replace("'","")

