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

from HTTPTransaction import *

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
# from mitmproxy.net.http import encoding

# Imported to use sys.exit when managing exceptions.
import sys

# Imported to instantiate HTTPLogger session attribute. (14/03/21)
from Session import *

"""
    HTTPLogger is the class that defines the addon for mitmproxy.
    The responsability of this class is to define methods to properly process
    http requests/responses: these methods should save important info such as
    headers or body as a JSON file that will be later used to train a machine
    learning algorithm.

    Marco, 09/01/21
"""


class HTTPLogger(object):
    def __init__(self, services=None, js_file=None, eos_file=None):
        if services is None:
            services = {}
        self.name = 'HTTPLogger Addon, by Marco Urbano'
        self.version = '2.2 -- 20/03/21'
        self.services = services
        # session attribute is an istance of Session. It contains all the info recorded during the session and will
        # be used to write all this info on the disk when the recording protocol ends. This attribute will initially
        # be instantiated as a clean session (the constructor with no parameters will set this object attributes with
        # empty strings or empty lists of objects). During the recording session it will contain all
        # the data related to current recording session and when the recording protocol ends it will be
        # cleaned again to make room for a new session.
        self.session = Session()

        # this boolean flag is employed to ensure a correct execution of the entire protocol.
        # Initially it is set to False. It will be enabled only when this class will notice that user asked to end
        # the recording session: in that case the protocol establishes that there is a final POST request
        # sent automatically from the user's browser to transmit the recorded session as JSON.
        self.waiting_for_json = False
        ''' 
            recording attribute is employed to track the state of the session.
            It can assume three different values:
            - "on": when recording is on this state it means that the session is gonna be recorded or the recording
                    is already taking place.
            - "off": when recording is on this state it means that everything that this addon is gonna intercept will
                     be not recorded.
            - "end_recording": when recording is on this state it means that last http request contained "record"
                               param set to false and that the proxy need to turn off the recording.
                               This state is distinguished from other two because when the user asks to stop the
                               recording we need to return him/her not the page him/her requested with the
                               record parameter set to false but a simple HTML page that informs that the recording
                               session has been successfully ended. 
        '''
        self.recording = "off"

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

        # we only open and store the webpage showed to the user when he/she ends the session once.
        # This webpage already contains the js contained in "action_recording_js"
        if eos_file is not None:
            try:
                html_stream = open(eos_file)
            except OSError:
                print(
                    "Could not open the file that contains the web page to show users when they finish the demonstration",
                    eos_file)
                sys.exit()
            with html_stream:
                self.EOS_webpage = html_stream.read()
        else:
            self.EOS_webpage = ''

    def request(self, flow):
        # Add host info (ip_addr, hostname) in 'services' dictionary if it has been seen for the first time.
        try:
            # check if ip_address is already present in 'services', if not we simply query the DNS to obtain info.
            self.services[flow.client_conn.ip_address[0]]
        except KeyError:
            # gethostbyaddr returns a triple (hostname, aliaslist, ipaddrlist).
            self.services[flow.client_conn.ip_address[0]] = socket.gethostbyaddr(flow.client_conn.ip_address[0])[0]

        # Case 1: this request is the final request of the exchange protocol. It contains all the actions performed
        #         by the penetration tester during the session in a JSON string.
        if flow.request.headers.get("content-type") == "application/json; charset=UTF-8" and self.waiting_for_json:
            # TODO: here the code to handle the JSON contained in the final request made automatically from the js.
            # Save user actions chain that has been received as JSON in self.session.
            self.session.end_user_actions = str(flow.request.content.decode())

            # Write recorded session in the output folder.
            self.session.save_session()
            # Set self.session == null to enable recording a new session. (Singleton pattern)
            self.session.clear()

            # set to False the attribute "waiting_for_json", with this operation the protocol ends successfully.
            self.waiting_for_json = False

        # Case 2: this request is not the final request containing the JSON describing the pentesting session.
        #         In this case we only need to check the request to start or stop the recording.
        else:
            # Managing attributes that will be employed to check if the recording is enabled or not.
            req_param = dict(flow.request.query)
            user_asked_to_record = False
            user_asked_to_stop_record = False

            '''
              Since the GET parameter "record" is not mandatory in every HTTP REQUEST, but only in the one that ask the
              proxy to start the recording session, we check if the request that is being processed contains the record
              parameter, if not we simply reset it to False because looking for a key that doesn't exist will
              raise a KeyError exception. '''
            try:
                # Case 1: first http req in which user asks the proxy to start the recording of the session.
                if req_param["record"] == "true":
                    user_asked_to_record = True
                # Case 2: last http req of the recording session in which the user asks the proxy to end the session
                elif req_param["record"] == "false":
                    user_asked_to_stop_record = True
            except KeyError:
                user_asked_to_record = False

            if user_asked_to_record and self.recording == "off":
                self.recording = "on"
            elif user_asked_to_stop_record and self.recording == "on":
                self.recording = "end_recording"

    # When handling a response we need to read not only the headers, but most importantly we
    # need to read the content of the message (the html page) because we need to observe what changes
    # take place (e.g. when an XSS exploit is used we need to read what is the content of the web page that
    # is vulnerable).
    # Note from the author (02/03): due to Selenium inability to inject javascript code in more than one page
    # (exactly the first page that we choose to open), this method will also be responsible of managing
    # the capture of user actions, captured by the event listeners.
    def response(self, flow):

        # Processing only HTTP successful responses (code 200).
        # Without this check we could record even pages that doesn't load for bad implementation. (e.g.
        # favicon.ico that doesn't load in the benchmark we used to test [wavsep])
        if flow.response.status_code == 200:
            # Save html response code to manipulate it later.
            html = BeautifulSoup(flow.response.text, 'html.parser')

            # Perform recording only if the request preceding this response is the first that contains "record"
            # parameter set to "true" or the recording has been enabled from a preceding request.
            if self.recording == "on":
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

                    # Instantiate session's attributes for the first time. If this response is not the first one
                    # that follows the request with "record=true" simply push the HTTPTransaction in the existing
                    # session.http_transaction list.
                    if self.session.task_name == "":
                        # Session class objects requires only url, task_name and start_time to be instantiated.
                        self.session.task_name = html.title.string if html.title is not None else "Empty Task Name"
                        self.session.start_time = datetime.now()
                        self.session.url = url_request

                        # TODO: remove this line of code if clear method works well
                        #self.session = Session(url_request, task_name, start_time)

                    # Save current transaction into session.http_transactions
                    self.session.http_transactions.append(HTTPTransaction(flow, self.services))

            # Case 2: http_response HTML will be altered with a simple HTML page that informs the user that
            #         the recording session has correctly been ended and provides him/her info about data recorded.
            elif self.recording == "end_recording":
                # TODO: here the code to manage the end of recording.
                html = BeautifulSoup(self.EOS_webpage, 'html.parser')
                self.recording = "off"
                # put the proxy server in a "listening for JSON" state. (take a look to the protocol)
                self.waiting_for_json = True

            # We need to inject javascript code that will be employed from
            # the browser to capture user actions (click, keyup, keydown, etc) before forwarding the reply .
            # 02/03/21 (trying to not use Selenium to record user actions)

            if self.action_recording_js != '':
                # Inject a script tag containing the JavaScript.
                container = html.head or html.body
                if container:
                    # Adding even an ID to the new tag to simply remove it from the records when writing the dataset.
                    script = html.new_tag('script', type='text/javascript', id='wapt_dataset_collector_record')
                    script.string = self.action_recording_js
                    container.insert(0, script)
                    flow.response.text = str(html)
                    print('Successfully injected the `injected-javascript.js` script.')
