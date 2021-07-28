import argparse
import configparser
import os
from pathlib import Path
import random
import requests
import smtplib
import time
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
delay = int(config['Integers']['delay'])

def replaced(mode, sequence, old, new):
    if mode == 'startswith':
        return (new if x.startswith(old) else x for x in sequence)

    if mode == 'in':
        return (new if old in x else x for x in sequence)

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


def send_phish(sender, msg_recipient, subject, phish, receiving_mta):
     message = MIMEMultipart()
     message["From"] = sender
     message["To"] = msg_recipient
     message["Subject"] = subject
     body = phish
     text = message.as_string()
     with smtplib.SMTP(receiving_mta) as server:
         server.sendmail(sender, msg_recipient, text)

def fire(msg_limit):
    msg_count = 1
    failed_count = 0
    while msg_count < msg_limit:
        spam = random.choice(os.listdir(spam_folder + '/'))
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
                                print('Failed: ' + str(e))
                                failed_count = failed_count + 1
                                continue
                        if 'Subject: ' in line:
                            try:
                                subject = line.split(':')[1]
                            except Exception as e:
                                print('Failed: ' + str(e))
                                failed_count = failed_count + 1
                                continue

            except Exception as e:
                print('Failed: ' + str(e))
                failed_count = failed_count + 1
                continue

            with open('message.current', 'r') as f:
                msg = f.read()
                msg = msg.encode('UTF-8')
                smtpObj = smtplib.SMTP(receiving_mta)
                try:
                    if (msg_count % 3 == 0):
                        malware = random.choice(os.listdir(malware_folder + '/'))
                        print('Sending message ' + str(msg_count) + ' of ' + str(msg_limit) + ' (Attaching malware file ' + malware + ')')
                        send_malware(sender, msg_recipient, subject, malware_folder + '/' + malware, receiving_mta)
                    else:
                        print('Sending message ' + str(msg_count) + ' of ' + str(msg_limit))
                        with smtplib.SMTP(receiving_mta) as server:
                            server.sendmail(sender, msg_recipient, msg)
                    #else:
                    #    print('Sending message ' + str(msg_count) + ' of ' + str(msg_limit))
                    #    with smtplib.SMTP(receiving_mta) as server:
                    #        server.sendmail(sender, msg_recipient, msg)
                
                except Exception as e:
                    print('Failed: ' + str(e))
                msg_count = msg_count + 1
                if delay > 0:
                    time.sleep(delay)
                if msg_count == msg_limit:
                    print('Messages sent: ' + str(msg_count) + '\nFailed: ' + str(failed_count))
                    sys.exit()


if __name__ == '__main__':
    if refresh_malware:
        malware_refresh(tg_api_key, tg_domain, malware_count)
    fire(msg_limit)
