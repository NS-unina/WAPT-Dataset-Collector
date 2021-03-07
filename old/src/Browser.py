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


class MyListener(AbstractEventListener):
    def __init__(self):
        self.url = 'empty'

    def before_navigate_to(self, url, driver):
        print("Before navigate to %s" % url)

    def after_navigate_to(self, url, driver):
        print("After navigate to %s" % url)
        print("Vecchio URL: " + self.curr_url + "Nuovo URL: " + driver.current_url)
        # #driver.save_screenshot("./image.png")

    def after_navigate_forward(self, driver):
        print("After navigate forward")

    def after_click(self, element, driver):
        print("after click!")

    def before_click(self, element, driver):
        print("before click!")


benchmark_name = socket.gethostbyname("localhost")
benchmark_port = 8888
benchmark_homepage = '/wavsep'

# Dinamically build up the url to request depending on the benchmark IP address, port and homepage
benchmark_url = 'http://' + benchmark_name + ':' + str(benchmark_port) + benchmark_homepage

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

addEventListeners_js = '''
start_time = new Date().getTime();

var recorder = {};
recorder.LISTENERS = [
                        'click',
                        'dblclick',
                        'mousedown',
                        'mouseup',
                        'keypress',
                        'keydown',
                        'keyup',
                        'scroll',
                     ];
                     
recorder.setup = function () {
  recorder.LISTENERS.forEach(function (name) {
    document.addEventListener(name, recorder['on' + name], true);
    document.addEventListener(name, recorder['on' + name], false);
  });
  var url = window.location.pathname;
  recorder.taskName = url.substr(url.lastIndexOf('/') + 1).replace(/\.html/, '');
  recorder.isSetup = true;
}

// Start recording the episode
recorder.startRecording = function () {
  recorder.data = {};
  recorder.data.taskName = recorder.taskName;
  recorder.data.states = [];
  recorder.isRecording = true;
  recorder.addState(null, null);
}

// Add a state to the recording data
recorder.addState = function (event, action) {
  if (event && action)
    action.timing = event.eventPhase;
  console.log('Adding state', action);
  var state = {
    'time': new Date().getTime() - start_time,
    'action': action,
  };
  if (event)
    event.target.dataset.recording_target = true;
  state.dom = document.documentElement.outerHTML;
  if (event)
    delete event.target.dataset.recording_target;
  recorder.data.states.push(state);
}

// Actions
recorder.ondblclick = function (event) {
  recorder.addState(event, {
    'type': 'dblclick',
    'x': event.pageX,
    'y': event.pageY,
  });
}
recorder.onclick = function (event) {
  recorder.addState(event, {
    'type': 'click',
    'x': event.pageX,
    'y': event.pageY,
  });
}
recorder.onmousedown = function (event) {
  recorder.addState(event, {
    'type': 'mousedown',
    'x': event.pageX,
    'y': event.pageY,
  });
}
recorder.onmouseup = function (event) {
  recorder.addState(event, {
    'type': 'mouseup',
    'x': event.pageX,
    'y': event.pageY,
  });
    localStorage["mouseup"] = "ok"
}

recorder.onkeypress = function (event) {
  recorder.addState(event, {
    'type': 'keypress',
    'keyCode': event.keyCode,
    'charCode': event.charCode,
    'humanReadable': String.fromCharCode(event.keyCode),
  });
}
recorder.onkeydown = function (event) {
  recorder.addState(event, {
    'type': 'keydown',
    'keyCode': event.keyCode,
    'charCode': event.charCode,
    'humanReadable': String.fromCharCode(event.keyCode),
  });
}
recorder.onkeyup = function (event) {
  recorder.addState(event, {
    'type': 'keyup',
    'keyCode': event.keyCode,
    'charCode': event.charCode,
    'humanReadable': String.fromCharCode(event.keyCode),
  });
}

recorder.onscroll = function (event) {
  // Scroll is super redundant; only keep the first one
  if (recorder.data.states.length) {
    var lastState = recorder.data.states[recorder.data.states.length - 1];
    if (lastState.action && lastState.action.type === 'scroll')
      return;
      //recorder.data.states.pop();     // <-- use this for keeping the last one
  }
  recorder.addState(event, {
    'type': 'scroll',
  });
}
window._getRecordedStates = function() { return recorder.data.states; };

// After that the previous code has been loaded, invoke record.startRecording to add the event listeners.
recorder.setup();
recorder.startRecording();
'''

# Javascript code seen in Huxley, catches too little events to be useful. It has been used to write _getRecordedStates.
# huxley_js = '''
# (function() {
# var events = [];
# window.addEventListener('click', function (e) { events.push([+new Date(), 'click', [e.clientX, e.clientY]]); }, true);
# window.addEventListener('keyup', function (e) { events.push([+new Date(), 'keyup',
#                                                                           String.fromCharCode(e.keyCode)]); }, true);
# window._getHuxleyEvents = function() { return events; };
# })();
# '''

ef_driver.execute_script(addEventListeners_js)
input("Press any key to quit.\n")
try:
    events = ef_driver.execute_script('return window._getRecordedStates();')
except:
    raise ValueError(
        'Could not call window._getRecordedStates(). ' +
        'This usually means you navigated to a new page, which is currently unsupported.'
    )

print(json.dumps(events, indent=2))

ef_driver.quit()


#driver.get("https://localhost:8888/wavsep/active/Reflected-XSS/RXSS-Detection-Evaluation-GET/Case03-Tag2TagStructure.jsp?userinput=textvalue")

