import requests

def url_checker(url):  # check if Url is valid
    res = requests.get(url)
    if str(res) == "<Response [200]>":
        print("Connection to Discogs established.\n")
        return True

    else:
        print("No Connection to Discogs possible...\n")
        return False