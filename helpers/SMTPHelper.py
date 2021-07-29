from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

class SMTPHandler(object):
    def __init__(self, receiving_mta, msg_recipient, sender):
        self.receiving_mta = receiving_mta
        self.msg_recipient = msg_recipient
    
    def sendMalware(self, sender, subject, malware):
        message = MIMEMultipart()
        message["From"] = sender
        message["To"] = self.msg_recipient
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
        with smtplib.SMTP(self.receiving_mta) as server:
            server.sendmail(sender, self.msg_recipient, text)

    def sendMessage(self, sender, subject, message):
        with smtplib.SMTP(self.receiving_mta) as server:
            server.sendmail(sender, self.msg_recipient, message)
    
    def sendPhish(self, subject, phish):
        message = MIMEMultipart()
        message["From"] = self.sender
        message["To"] = self.msg_recipient
        message["Subject"] = subject
        body = phish
        text = message.as_string()
        with smtplib.SMTP(self.receiving_mta) as server:
            server.sendmail(self.sender, self.msg_recipient, text)