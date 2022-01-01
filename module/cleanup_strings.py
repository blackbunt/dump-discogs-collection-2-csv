# -*- coding: utf-8 -*-
"""
This module cleans up artist and release title strings for file creation as XLS and CSV. It also does additional
adjustments for URL-generation.
"""

import re
import logging

logger = logging.getLogger()

def cleanup_artist(input: str) -> str:
    """
    Removes the digits an artist name has in case the artist name has several occurances on Discogs.
    :param input: Artist
    :type input: String
    :return: Artist
    :rtype: String
    """

    artist = re.sub("[(]+[\d+]+[)]+$", "", input)
    artist = artist.rstrip()

    logger.debug(input + " -> " + artist)
    return artist


def cleanup_artist_url(input: str) -> str:
    """
    Adjusts artist name for usage in URL.
    :param input: Artist
    :type input: String
    :return: Artist
    :rtype: String
    """

    artist = cleanup_artist(input)
    artist = cleanup_for_url(artist)

    logger.debug(input + " -> " + artist)
    return artist


def cleanup_title(input: str) -> str:
    """
    Removes slash, digits in brackets and other unwanted characters from release title.
    :param input: Release title
    :type input: String
    :return: Release title
    :rtype: String
    """
    # TODO Check if same for artist and simplify

    title = re.sub(" / ", "-", input)
    title = re.sub("[(]+[\d+]+[)]+$", "", title)
    title = re.sub("\W+(?![^-])", "-", title)
    title = re.sub("[-]+$", "", title)
    title = re.sub("/", "-", title)

    logger.debug(input + " -> " + title)
    return title

def cleanup_title_url(input: str) -> str:
    """
    Adjusts release title name for usage in URL.
    :param input: Release title
    :type input: String
    :return: Release title
    :rtype: String
    """

    title = cleanup_title(input)
    title = cleanup_for_url(title)

    logger.debug(input + " -> " + title)
    return title

def cleanup_styles(input: str) -> str:
    """
    Removes square brackets and single quotes from the styles entry.
    :param input: Music styles
    :type input: String
    :return: Music styles
    :rtype: String
    """

    return input.replace("[", "").replace("]", "").replace("'", "")


def cleanup_for_url(input: str) -> str:
    """
    Replaces the following characters with a hyphen for usage in a URL:
    - slash
    - any character that is not a word character (alphanumeric & underscore)
    - everything that is not a word
    - empty space
    and removes the following characters without replacement:
    - number sign
    - hyphen at the end of the string

    :param input: Input
    :type input: String
    :return: Output
    :rtype: String
    """

    input = re.sub(" / ", "-", input)
    input = re.sub("\W+(?![^-])", "-", input)
    input = re.sub("[-]+$", "", input)
    input = re.sub("/", "-", input)
    input = re.sub(" ", "-", input)
    input = re.sub("#", "", input)

    return input
