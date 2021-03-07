# Author: Marco Urbano.
# Date: 21 January 2021. (HttpLogger, that was previously named HttpInterceptor, was originally written in the main
#                         script file on 08/01/20).
# Description: this simple script defines the main addon used to record http requests/responses as .JSON file.
# Notes:
#           To save http requests as JSON:
# https://stackoverflow.com/questions/59730848/how-to-catch-response-of-server-in-mitmproxy-container-and-past-it-into-file-in


# Datetime is useful due to its now() function: it will be used when creating a new file with a request/response
# intercepted. Without this function we should name a request to the same URI with a progressive number (e.g.
# localhost_wavsep_1, localhost_wavsep_2, ..., localhost_wavsep_n).
from datetime import datetime

from HTTPRecord import *

# Initially used to invoke "mkdir" to create the dataset folder.
import os
import errno

# Used to save files specifying the path (a directory that differs from the cwd)
from pathlib import Path

# Added 14/01/21, could be useful to read request and response.
# from mitmproxy.net.http.http1.assemble import assemble_request, assemble_response, _assemble_request_headers

# Used to parse html content of the http_response and to get the title.
# Class myParser is a subclass of HTTPParser of html library.
from Parser import Parser

# Beatifulsoup will be employed to quickly manipulate the response with the aim to add javascript to it.
from bs4 import BeautifulSoup

# Added to decode flow.response to add js code.
from mitmproxy.net.http import encoding

# Imported to use sys.exit when managing exceptions.
import sys

"""
    HTTPLogger is the class that defines the addon for mitmproxy.
    The responsability of this class is to define methods to properly process
    http requests/responses: these methods should save important info such as
    headers or body as a JSON file that will be later used to train a machine
    learning algorithm.

    Marco, 09/01/21
"""


class HTTPLogger(object):
    def __init__(self, services=None, js_file=None):
        if services is None:
            services = {}
        self.name = 'HTTPLogger Addon, by Marco Urbano'
        self.version = '2.0 -- 02/03/21'
        self.services = services

        # recording is a flag that will be set to True if the request intercepted contained "record"
        # parameter set to "true". This attribute remains set to True through all the recording session.
        # When the recording session ends (this happens when the user make a request with "record" attribute
        # set to "false") the proxy will record no more (till the next request containing the record parameter
        # set to true, then the cycle begins again).
        self.recording = False

        # action_recording_js is the javascript code that will be injected to every page visited from the pentester.
        if js_file is not None:
            try:
                js_stream = open(js_file)
            except OSError:
                print("Could not open the file that contains javascript code to record user actions", js_file)
                sys.exit()
            with js_stream:
                self.action_recording_js = js_stream.read()
        else:
            self.action_recording_js = ''

    # Uncomment if is needed to trigger some event when a request is intercepted.
    def request(self, flow):
        # Add host info (ip_addr, hostname) in 'services' dictionary if it has been seen for the first time.
        try:
            # check if ip_address is already present in 'services', if not we simply query the DNS to obtain info.
            self.services[flow.client_conn.ip_address[0]]
        except KeyError:
            # gethostbyaddr returns a triple (hostname, aliaslist, ipaddrlist).
            self.services[flow.client_conn.ip_address[0]] = socket.gethostbyaddr(flow.client_conn.ip_address[0])[0]

        # Managing attributes that will be employed to check if the recording is enabled or not.
        req_param = dict(flow.request.query)
        # Flag to set to 1 if the request is the first that asks to start the recording session.
        user_asked_to_record = False
        # Looking for a key that doesn't exist will raise a KeyError exception.
        try:
            if req_param["record"] == "true":
                user_asked_to_record = True
        except KeyError:
            user_asked_to_record = False

        if user_asked_to_record and self.recording is not True:
            self.recording = True

    # When handling a response we need to read not only the headers, but most importantly we
    # need to read the content of the message (the html page) because we need to observe what changes
    # take place (e.g. when an XSS exploit is used we need to read what is the content of the web page that
    # is vulnerable).
    # Note from the author (02/03): due to Selenium inability to inject javascript code in more than one page
    # (exactly the first page that we choose to open), this method will also be responsible of managing
    # the capture of user actions, captured by the event listeners.

    def response(self, flow):
        # Processing only HTML successful responses (code 200).
        # Without this check we could record even pages that doesn't load for bad implementation. (e.g.
        # favicon.ico that doesn't load like in wavsep)
        if flow.response.status_code == 200:
            # Perform recording only if the request preceding this response is the first that contains "record"
            # parameter set to "true" or the recording has been enabled from a preceding request.
            if self.recording:
                # Here the concept of "Variable Annotation" is used to specify that variable named
                # "url_request" is a string.
                # To know more about Variable Annotation see: https://www.python.org/dev/peps/pep-0526/
                url_request: str = str(flow.request.pretty_url)

                """
                    ISSUE: CHECK IF THE IF STATEMENT ON STATIC CAN BE OMITTED.
            
                    Marco, 10/01/2020 23.39
                """
                if '/static/' not in url_request:
                    # Uncomment to use the url as the name of the recorded http response.
                    # url_request = url_request.replace("/", "_")

                    # Invoking parser to obtain html document title.
                    html_parser = Parser()
                    html_content = flow.response.content.decode()
                    html_parser.feed(html_content)
                    html_title = html_parser.get_title()

                    # data_folder will be located outside of the current folder (named src/)
                    data_folder = Path("../out/http_dataset/")
                    # Every intercepted request will be labeled with the name of the resource requested
                    # plus the current datetime (YYYY-MM-DD HH:MM:SS.DS).
                    current_filename = html_title + '-' + str(datetime.now()) + '.json'
                    file_to_open = data_folder / current_filename

                    # Create the directory named "http_dataset" with the first usage.
                    if not os.path.exists(os.path.dirname(file_to_open)):
                        try:
                            os.makedirs(os.path.dirname(file_to_open))
                        except OSError as exc:  # Guard against race condition
                            if exc.errno != errno.EEXIST:
                                raise

                    # Just a little syntaptic sugar: could be written without the "with ... as ..."
                    # but doing this way the opened file will be closed after the manipulation.
                    with open(file_to_open, "w") as record:

                        # MyHttpRecord constructor will extract all the data from flow object.
                        # Doing so the code will result cleaner to read.
                        http_record = HTTPRecord(flow, self.services)
                        record.write(http_record.getJSON())

            # We need to inject javascript code that will be employed from
            # the browser to capture user actions (click, keyup, keydown, etc) before forwarding the reply .
            # 02/03/21 (trying to not use Selenium to record user actions)

            if self.action_recording_js != '':
                # Inject a script tag containing the JavaScript.
                html = BeautifulSoup(flow.response.text, 'html')
                container = html.head or html.body
                if container:
                    script = html.new_tag('script', type='text/javascript')
                    script.string = self.action_recording_js
                    container.insert(0, script)
                    flow.response.text = str(html)
                    print('Successfully injected the `injected-javascript.js` script.')