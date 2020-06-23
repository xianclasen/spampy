# spampy

Spampy is designed for testing email security solutions by sending large amounts of spam and malware to a given email address. It has few required pre-requisites if it is to work "as-written..."

1. A Cisco Threat Grid API key for pulling down and re-packaging malware (or you can fill the malware-source folder yourself).
2. A working and initialized Metasploit installation to re-package the downloaded malware samples (or you can fill the malware-source folder yourself).
3. An SMTP server which allows you to relay mail to the destination without authentication (local instances such as postfix or remote MTAs will work).

<h1>The config file</h1>

You must specify a config file at runtime thusly:

    ./spampy.py /path/to/config.ini

An example config file is provided and the values should be self-explanatory. You must add custom values before the script will work for you.

Sourcing the spam and malware

The spam-source folder contains spam  messages that will be re-addressed to the recipient of choice and packed with malware. The folder is seeded with messages but I would suggest filling it with more. The source of my spam is Bruce's archive over at Untroubled (http://untroubled.org/spam/).

The malware is pulled from the top 100 malicious samples from Threat Grid and re-packaged using MSFVenom into EXE files. There is an option in the config file to refresh the malware source folder with new files at runtime. This adds significant time to the overall operation. Malware is attached to every 3rd message sent.
