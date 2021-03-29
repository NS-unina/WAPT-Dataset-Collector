# Author: Marco Urbano.
# Date: 29 March 2021.
# Description: this class has the responsibility to read the .JSON file produced by WAPT-Dataset-Collector and to
#              to replay it by means of Selenium webdriver.
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

import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import re


class Player(object):
    keyValues = {'Backspace': Keys.BACKSPACE, 'Tab': Keys.TAB, 'Enter': Keys.ENTER, 'Shift': Keys.SHIFT,
                 'Control': Keys.CONTROL, 'Alt': Keys.ALT, 'Pause': Keys.PAUSE, 'Escape': Keys.ESCAPE, ' ': Keys.SPACE,
                 'PageUp': Keys.PAGE_UP, 'PageDown': Keys.PAGE_DOWN, 'End': Keys.END, 'Home': Keys.HOME,
                 'ArrowLeft': Keys.ARROW_LEFT, 'ArrowUp': Keys.ARROW_UP, 'ArrowRight': Keys.ARROW_RIGHT,
                 'ArrowDown': Keys.ARROW_DOWN, 'Insert': Keys.INSERT, 'Delete': Keys.DELETE}

    # keyValues['CapsLock'] = not found
    # keyValues['PrintScreen'] = not found

    def __init__(self, rec_filename):
        # using time_elapsed to execute actions at the same time of the original recording: time is expressed in ms.
        self.time_elapsed = 0

        self.session = {}
        rec_file = None
        # proceed only if -recording is not null, a recording to be reproduced must be provided.
        try:
            rec_file = open(rec_filename, 'r')
        except OSError:
            print("Could not open/read file:", rec_file)
            sys.exit()

        with rec_file:
            # obtaining the json file as a dictionary.
            self.session = json.load(rec_file)

        # instantiating webdriver and setting options.
        chrome_options = webdriver.ChromeOptions()
        # set window size as maximum size
        # chrome_options.add_argument('start-maximized')
        # set window size as the same used during the recording.
        chrome_options.add_argument("--window-size=" + self.session.pop('window_width') + ","
                                                     + self.session.pop('window_height'))
        # set window position centered.
        chrome_options.add_argument("--window-position=0,0")

        # Default settings to avoid crashes during the chromedriver execution. (source: stackoverflow)
        # disabling infobars
        chrome_options.add_argument("disable-infobars")
        # workaround to avoid "selenium.common.exceptions.WebDriverException: DevToolsActivePort file doesn't exist"
        chrome_options.add_argument("--remote-debugging-port=8320")
        # disabling extensions
        chrome_options.add_argument("--disable-extensions")
        # overcome limited resource problems
        chrome_options.add_argument("--disable-dev-shm-usage")
        # This is a workaround to avoid crashes: it bypasses OS security model.
        chrome_options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(options=chrome_options)
        # the empty action_chain that will contain the sequence of action performed by the user.
        self.action_chain = ActionChains(self.driver)

        # build the action chain.
        # self.__build_action_chain()

    # this method gets as input parameter a dict called "action" and selects the correct action to add to the
    # action_chain
    def __add_action(self, action):
        # since the actions are not performed one after the other immediately we need to consider the timing of each
        # action.
        ms_to_wait = action["time"] - self.time_elapsed
        self.action_chain.pause(ms_to_wait / 1000)
        self.time_elapsed = action["time"]

        if action["action"]["type"] == "keydown" or action["action"]["type"] == "keyup":
            try:
                key_up_down = self.keyValues[action["action"]["key"]]
                if action["action"]["type"] == "keydown":
                    self.action_chain.key_down(key_up_down)
                else:
                    self.action_chain.key_up(key_up_down)
            except KeyError:
                # if action["key"] is not present in the list of special keys supported by Selenium
                # try to make the key_up/key_down action with the character itself.
                #key_up_down = action["action"]["key"]
                pass

        elif action["action"]["type"] == "keypress":
            self.action_chain.send_keys(action["action"]["key"])
        elif action["action"]["type"] == "click" or action["action"]["type"] == "dbclick":
            self.action_chain.move_by_offset(action["action"]["x"], action["action"]["y"])
            if action["action"]["type"] == "click":
                # TODO: check if it is necessary to reset the cursor position to solve the MoveTargetOutOfBoundException
                self.action_chain.click().move_by_offset(-action["action"]["x"], -action["action"]["y"])
            else:
                self.action_chain.double_click()

    def replay_actions(self):
        for k, v in self.session['transactions'].items():
            curr_url = v['url']
            # since the container changes IP every time that the network is restarted and the 'penetration_net' has been
            # designed to expose the benchmark container port even on localhost, we substitute the container IP ADDRESS
            # with localhost. Without doing this we could not be able to reproduce a recording that has the benchmark
            # IP ADDRESS that differs from the current benchmark IP ADDRESS.
            curr_url = re.sub(r'\/\/\d*\.\d*\.\d*\.\d:', '//localhost:', curr_url)
            # print(curr_url)
            # add every action to the action_chain.
            for k_action, v_action in v['actions'].items():
                # print(v_action['action']['type'])
                self.__add_action(v_action)

            # TODO: here we need a check to caption if the webpage has been navigated manually
            #       as in the case of a Reflected XSS, or if it has been navigated just simply
            #       by clicking some button or link.
            if k != "1":
                if self.driver.current_url != curr_url:
                    self.driver.get(curr_url)
            else:
                self.driver.get(curr_url)

            self.action_chain.perform()
            self.action_chain.reset_actions()

        # quit the driver after the action chain for every transaction has ended.
        #time.sleep(5)
        self.driver.quit()
