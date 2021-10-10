# Cleans up Artist and Title strings for Url Generartion and for .csv file

import re

DEBUG = False

def cleanup_artist(artist):  # removes "( digit )"
    artist = re.sub("[(]+[\d+]+[)]+$", "", artist)
    artist = artist.rstrip()
    return artist


def cleanup_artist_url(artist):  # url-generatrion

    artist = cleanup_artist(artist)
    artist = cleanup_for_url(artist)

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

    title = cleanup_for_url(title)

    if DEBUG: print("title: " + title)
        
    return title

def cleanup_styles(styles):

    return styles.replace("[","").replace("]","").replace("'","")


def cleanup_for_url(input):

    input = re.sub(" / ", "-", input)
    input = re.sub("\W+(?![^-])", "-", input)
    input = re.sub("[-]+$", "", input)
    input = re.sub("/", "-", input)
    input = re.sub(" ", "-", input)
    input = re.sub("#", "", input)

    return input
