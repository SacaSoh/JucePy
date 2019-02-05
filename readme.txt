JucePy
Project executed as Harvard CS50x Introduction to Computer Science final project.

A State of Ceará, Brazil, Trade Board process tracker database.
JucePy automatically updates a database with a process history - you can keep track of everything without manually going
to JUCEC website every hour :-)


USAGE:

After installing the required modules and prerequisites as below, **and setting FLASK_APP environment variable***,
just execute on command line (bash, CMD, Powershell) the command:

"flask run --port=8080" (to keep access for only your machine) or:
"flask run --host=0.0.0.0 --port=8080" (to give access to your network)

The it can be accessed at  your browser with by SERVERIP:8080

For windows, the file "RUN.bat" automatically runs set the flask env and run the server (exposed to network), given that
required modules, etc, are correctly installed.

REQUIREMENTS:

1. To install module requirements just run the command: "pip install -r requirements.txt"

2. Before running the script, remember to change FLASK_APP environment variable:

    On Unix Bash (Linux, Mac, etc.):

    $ export FLASK_APP=application
    $ flask run

    On Windows CMD:

    > set FLASK_APP=application
    > flask run

    On Windows PowerShell:

    > $env:FLASK_APP = "application"
    > flask run

3. Chrome webdriver:

a) Instructions for linux install (working with below mentioned versions - in case of error look for updated versions):
(Instructions can be found on https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/ but beware that's java oriented)

    1. X virtual framebuffer:

    sudo apt-get update
    sudo apt-get install -y unzip xvfb libxi6 libgconf-2-4

    2. Google Chrome:

    sudo curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
    sudo echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
    sudo apt-get -y update
    sudo apt-get -y install google-chrome-stable

    3. Chromedriver:

    wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip
    unzip chromedriver_linux64.zip

    3.1 Chromedriver config:

    sudo mv chromedriver /usr/bin/chromedriver
    sudo chown root:root /usr/bin/chromedriver
    sudo chmod +x /usr/bin/chromedriver

b) Instructions for Windows Install:

    1. Chromedriver

    http://chromedriver.chromium.org/downloads/

    Just get last version and put in yor "C:/" or "C:/Windows" directory.