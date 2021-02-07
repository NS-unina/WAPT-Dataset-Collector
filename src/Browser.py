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

benchmark_name = socket.gethostbyname("localhost")
benchmark_port = 8888
benchmark_homepage = '/wavsep'

# Dinamically build up the url to request depending on the benchmark IP address, port and homepage
benchmark_url = 'http://' + benchmark_name + ':' + str(benchmark_port) + benchmark_homepage

chrome_options = webdriver.ChromeOptions()

# open Browser in maximized mode
chrome_options.add_argument('start-maximized')
# disabling infobars
chrome_options.add_argument("disable-infobars")
# workaround to avoid "selenium.common.exceptions.WebDriverException: DevToolsActivePort file doesn't exist"
chrome_options.add_argument("--remote-debugging-port=9224")
# disabling extensions
chrome_options.add_argument("--disable-extensions")
# overcome limited resource problems
chrome_options.add_argument("--disable-dev-shm-usage")
# This is a workaround to avoid crashes: it bypasses OS security model.
chrome_options.add_argument("--no-sandbox");

driver = webdriver.Chrome(options=chrome_options)

driver.execute_script('''
(function() {
var events = [];
window.addEventListener('click', function (e) { events.push([+new Date(), 'click', [e.clientX, e.clientY]]); }, true);
window.addEventListener('keyup', function (e) { events.push([+new Date(), 'keyup', String.fromCharCode(e.keyCode)]); }, true);
window._getHuxleyEvents = function() { return events; };
})();
''')

driver.get("https://localhost:8888/wavsep/index-active.jsp")
