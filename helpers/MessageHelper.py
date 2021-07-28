import random
import os


class MessageHandler(object):
    def __init__(self, msg_recipient, spam_folder):
        self.spam_folder = spam_folder
        self.msg_recipient = msg_recipient
    
    def createCurrentMessage(self):
        spam = random.choice(os.listdir(self.spam_folder + '/'))
        with open(self.spam_folder + '/' + spam, encoding = "ISO-8859-1") as m:
            try:
                lines = m.readlines()
                with open('message.current', 'w') as f:
                    msg = self.replaced('startswith', lines, 'To: ', 'To: ' + self.msg_recipient + '\n')
                    f.write("".join(msg))
                    for line in lines:
                        if 'From: ' in line:
                            try:
                                sender = line.split(':')[1]
                                sender = sender.split('<')[1]
                                sender = sender.split('>')[0]
                            except Exception as e:
                                print('Failed: ' + str(e))
                                return 'Failed'
                        if 'Subject: ' in line:
                            try:
                                subject = line.split(':')[1]
                            except Exception as e:
                                print('Failed: ' + str(e))
                                return 'Failed'
            
            except Exception as e:
                print('Failed: ' + str(e))
                return 'failed'

        return sender, subject

    def replaced(self, mode, sequence, old, new):
        if mode == 'startswith':
            return (new if x.startswith(old) else x for x in sequence)

        if mode == 'in':
            return (new if old in x else x for x in sequence)