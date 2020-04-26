import requests

def url_checker(url):  # check if Url is valid
    res = requests.get(url)
    if str(res) == "<Response [200]>":
        return True

    else:
        return False