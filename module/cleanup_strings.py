# Cleans up Artist and Title strings for Url Generartion and for .csv file

import re
import logging

logger = logging.getLogger()

def cleanup_artist(artist):  # removes "( digit )"

    a = re.sub("[(]+[\d+]+[)]+$", "", artist)
    a = a.rstrip()

    logger.debug(artist + " -> " + a)
    return a


def cleanup_artist_url(artist):  # url-generatrion

    a = cleanup_artist(artist)
    a = cleanup_for_url(a)

    logger.debug(artist + " -> " + a)
    return a


def cleanup_title(title):

    t = re.sub(" / ", "-", title)
    t = re.sub("[(]+[\d+]+[)]+$", "", t)
    t = re.sub("\W+(?![^-])", "-", t)
    t = re.sub("[-]+$", "", t)
    t = re.sub("/", "-", t)

    logger.debug(title + " -> " + t)
    return t

def cleanup_title_url(title):

    t = cleanup_title(title)
    t = cleanup_for_url(t)

    logger.debug(title + " -> " + t)
    return t

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
