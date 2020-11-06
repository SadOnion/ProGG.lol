import requests
import urllib3

urllib3.disable_warnings()

URL = "https://127.0.0.1:2999/liveclientdata/"


def request(url):
    return requests.get(URL + url, verify=False)
