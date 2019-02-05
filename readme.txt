JucePy
Project executed as Harvard CS50x Introduction to Computer Science final project.

A State of Ceará, Brazil, Trade Board process tracker database.
JucePy automatically updates a database with a process history - you can keep track of everything without manually going
to JUCEC website every hour :-)

JucePy runs as a server and keeps the processes info at a database, so multiple user can interact with it simultaneously


USAGE:

After installing the required modules and prerequisites as below, **and setting FLASK_APP environment variable***,
just execute on command line (bash, CMD, Powershell) the command:

"flask run --port=8080" (to keep access for only your machine) or:
"flask run --host=0.0.0.0 --port=8080" (to give access to your network)

Then it can be accessed at your browser with by SERVERIP:8080

For windows, the file "RUN.bat" automatically runs set the flask env and run the server (exposed to network), given that
required modules, etc, are correctly installed.

REQUIREMENTS:

1. Install Python - https://www.python.org/downloads/

2. To install module requirements go to the install folder and  run the command: "pip install -r requirements.txt"

3. Before running the script, remember to change FLASK_APP environment variable:

    3.1 On Unix Bash (Linux, Mac, etc.):

    $ export FLASK_APP=application
    $ flask run

    3.2 On Windows CMD:

    > set FLASK_APP=application
    > flask run

    3.3 On Windows PowerShell:

    > $env:FLASK_APP = "application"
    > flask run

4. Chrome webdriver:

4.1 Instructions for linux install (working with below mentioned versions - in case of error look for updated versions):
(Instructions can be found on https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/ but beware that's java oriented)

    4.1.1. X virtual framebuffer:

    sudo apt-get update
    sudo apt-get install -y unzip xvfb libxi6 libgconf-2-4

    4.1.2. Google Chrome:

    sudo curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
    sudo echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
    sudo apt-get -y update
    sudo apt-get -y install google-chrome-stable

    4.1.3. Chromedriver:

    wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip
    unzip chromedriver_linux64.zip

    4.1.4. Chromedriver config:

    sudo mv chromedriver /usr/bin/chromedriver
    sudo chown root:root /usr/bin/chromedriver
    sudo chmod +x /usr/bin/chromedriver

4.2 Instructions for Windows Install:

    4.2.1. Chromedriver

    http://chromedriver.chromium.org/downloads/

    Just get last version and put in yor "C:/" or "C:/Windows" directory.