import argparse
import configparser
import os
import random
from helpers.SMTPHelper import SMTPHandler
from helpers.MessageHelper import MessageHandler
from helpers.TGHelper import TGHandler
import sys
import time

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

def fire(msg_limit):
    msg_count = 1
    failed_count = 0
    MH = MessageHandler(msg_recipient, spam_folder)
    while msg_count < msg_limit:
        sender, subject = MH.createCurrentMessage()
        SH = SMTPHandler(receiving_mta, msg_recipient, sender)
        with open('message.current', 'r') as f:
            message = f.read()
            message = message.encode('UTF-8')
            try:
                if (msg_count % 3 == 0):
                    malware = random.choice(os.listdir(malware_folder + '/'))
                    print('Sending message ' + str(msg_count) + ' of ' + str(msg_limit) + ' (Attaching malware file ' + malware + ')')
                    SH.sendMalware(sender, subject, subject, malware)
                else:
                    print('Sending message ' + str(msg_count) + ' of ' + str(msg_limit))
                    SH.sendMessage(sender, subject, message)
            
            except Exception as e:
                print('Failed: ' + str(e))
                failed_count = failed_count + 1
            msg_count = msg_count + 1
            if delay > 0:
                time.sleep(delay)
            if msg_count == msg_limit:
                print('Messages sent: ' + str(msg_count) + '\nFailed: ' + str(failed_count))
                sys.exit()


if __name__ == '__main__':
    if refresh_malware:
        TH = TGHandler(tg_api_key, tg_domain, malware_folder)
        TH.refreshMalware(malware_count)
    fire(msg_limit)
