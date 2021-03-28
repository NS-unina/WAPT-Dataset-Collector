# Author: Marco Urbano.
# Date: 30 January 2021.
# Description: this file contains the script that performs the DOM recording for every action performed by the pentester
# Notes:
# https://stackoverflow.com/questions/42478591/python-selenium-chrome-webdriver
# https://stackoverflow.com/questions/35884230/can-my-webdriver-script-catch-a-event-from-the-webpage
#
# Useful list of action chain event keys. The list of keys will be needed to choose, for example, which key must be
# pressed when the browser listened to keyup, keydown or keypress event.
# https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.common.action_chains
# https://www.freecodecamp.org/news/javascript-keycode-list-keypress-event-key-codes/

# importing webdriver from selenium
from selenium import webdriver
import chromedriver_binary
import sys
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
import json
from selenium.webdriver.common.by import By

import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# Command line argument parser.
import argparse


# delegate parsing task to argparse library.
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-recording", "--recording", default='null',
                        help="recording must contain the name of the file that contain the recording to reproduce."
                             + "WAPT-Dataset-Collector saves recording files in out/ folder.")
args = arg_parser.parse_args()

# dictionary that contains the JSON file r
record_dict = {}
# proceed only if -recording is not null, a recording to be reproduced must be provided.
if args.recording != 'null':
    try:
        rec_file = open(args.recording, 'r')
    except OSError:
        print("Could not open/read file:", args.recording)
        sys.exit()

    with rec_file:
        # obtaining the json file as a dictionary.
        record_dict = json.load(rec_file)

    # obtain window height and width to open a window of the same dimension opened during the recording.
    window_height = record_dict.pop('window_height')
    window_width = record_dict.pop('window_width')


    chrome_options = webdriver.ChromeOptions()
    # open Browser in maximized mode
    #chrome_options.add_argument('start-maximized')

    # disabling infobars
    chrome_options.add_argument("disable-infobars")
    # workaround to avoid "selenium.common.exceptions.WebDriverException: DevToolsActivePort file doesn't exist"
    chrome_options.add_argument("--remote-debugging-port=9028")
    # disabling extensions
    chrome_options.add_argument("--disable-extensions")
    # overcome limited resource problems
    chrome_options.add_argument("--disable-dev-shm-usage")
    # This is a workaround to avoid crashes: it bypasses OS security model.
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)

    driver.set_window_position(0, 0)
    driver.set_window_size(window_width, window_height)

    for k, v in record_dict['transactions'].items():
        curr_url = v['url']
        print(curr_url)
        for k2, v2 in v['actions'].items():
            print(v2['action']['type'])

            # TODO: check every action and add it to the ActionChains(driver) as in the comment below.
            #       Use the list of key names to add the right Keys element when calling key_down, key_up, key_press.



    #driver.get('http://172.19.0.2:8080/wavsep/active/Reflected-XSS/RXSS-Detection-Evaluation-GET/Case02-Tag2TagScope.jsp?userinput=textvalue&record=true')
    #ActionChains(driver).move_by_offset(92, 35).click().key_down(Keys.BACKSPACE).send_keys('c').pause(1).send_keys('i').send_keys('a').send_keys('o').perform()

    #time.sleep(10) # Pause to allow you to inspect the browser.
    #driver.quit()


#driver.get("https://localhost:8888/wavsep/active/Reflected-XSS/RXSS-Detection-Evaluation-GET/Case03-Tag2TagStructure.jsp?userinput=textvalue")

