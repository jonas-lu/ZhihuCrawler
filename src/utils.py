import requests

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'}

def get_session():
    s = requests.session()
    s.headers.update(HEADERS)
    return s

def download_page(url):
    return requests.get(url, headers = HEADERS).content