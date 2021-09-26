import cleanup_strings as clean
from functools import partial

# Set jsonpath_ng strings
def set_json():
    structure = {}

    # Styles
    structure['styles_raw'] = '$.basic_information.styles'

    # Format
    structure['format_raw'] = '$.basic_information.formats[0].descriptions'

    # Album title
    structure['album_title'] = '$.basic_information.title'

    # Discogs-ID (str)
    structure['discogs_no'] = '$.basic_information.id'

    # Artist
    structure['artist_raw'] = '$.basic_information.artists[0].name'

    # Release Year
    structure['year'] = '$.basic_information.year'

    # Label Name
    structure['label'] = '$.basic_information.labels[0].name'

    # Catalog Number
    structure['catalog_no'] = '$.basic_information.labels[0].catno'

    # Genres
    structure['genres'] = '$.basic_information.genres[0]'

    # Date Added
    structure['date_added'] = '$.date_added'

    # Rating
    structure['rating'] = '$.rating'

    # Low-Res Cover Art Url
    structure['cover_low_url'] = '$.basic_information.thumb'

    # Full-Res Cover Art Url
    structure['cover_full_url'] = '$.basic_information.cover_image'

    # Media Condition
    structure['media_condition'] = '$.notes[0].value'

    # Sleeve Condition
    structure['sleeve_condition'] = '$.notes[1].value'

    return structure

# Initialize options for processing after loading and initalize jsonpath_ng
def set_all():

    processing = {}
    processing_set = {'styles', 'format', 'artist'}

    for i in processing_set:
        processing[i] = 'NOTPROCESSED'

    options = {'styles': partial(clean.cleanup_styles),
               'format': partial(clean.cleanup_styles),
               'artist': partial(clean.cleanup_artist)}

    return set_json(), options, processing