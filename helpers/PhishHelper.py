import os
import requests

class PhishHandler(object):
    def __init__(self, url):
        self.url = url
    
    def RefreshPhish(self, phish_folder):
        phish_file = phish_folder + '/phishes.txt'
        if os.path.exists(phish_file):
            os.remove(phish_file)
        resp = requests.get(self.url)
        with open(phish_folder + '/phishes.txt', 'wb') as f:
            f.write(resp.content)