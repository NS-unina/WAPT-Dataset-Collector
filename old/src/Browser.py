# Author: Marco Urbano.
# Date: 30 January 2021.
# Description: this file contains the script that performs the DOM recording for every action performed by the pentester
# Notes:
# https://stackoverflow.com/questions/42478591/python-selenium-chrome-webdriver
# https://stackoverflow.com/questions/35884230/can-my-webdriver-script-catch-a-event-from-the-webpage
#
#

# importing webdriver from selenium
from selenium import webdriver
import chromedriver_binary
import socket
import sys
from selenium.webdriver.support.events import EventFiringWebDriver, AbstractEventListener
import json
from selenium.webdriver.common.by import By

import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


#benchmark_name = socket.gethostbyname("localhost")
#benchmark_port = 8888
#benchmark_homepage = '/wavsep'

# Dinamically build up the url to request depending on the benchmark IP address, port and homepage
#benchmark_url = 'http://' + benchmark_name + ':' + str(benchmark_port) + benchmark_homepage

#page_to_test = input("Insert the URI that contains the webpage to test. The recording will be found in a folder" +
#                     "that contains the title of the page plus the timestamp.\n:")

chrome_options = webdriver.ChromeOptions()

# open Browser in maximized mode
chrome_options.add_argument('start-maximized')
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
event_listener = MyListener()
ef_driver = EventFiringWebDriver(driver, event_listener)



driver = webdriver.Chrome()

driver.get('http://google.com')
element = driver.find_element_by_link_text('About')

ActionChains(driver) \
    .key_down(Keys.CONTROL) \
    .click(element) \
    .key_up(Keys.CONTROL) \
    .perform()

time.sleep(10) # Pause to allow you to inspect the browser.

driver.quit()

ef_driver.quit()


#driver.get("https://localhost:8888/wavsep/active/Reflected-XSS/RXSS-Detection-Evaluation-GET/Case03-Tag2TagStructure.jsp?userinput=textvalue")

