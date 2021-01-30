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


"""
    HTTPLogger is the class that defines the addon for mitmproxy.
    The responsability of this class is to define methods to properly process
    http requests/responses: these methods should save important info such as
    headers or body as a JSON file that will be later used to train a machine
    learning algorithm.

    Marco, 09/01/21
"""


class HTTPLogger(object):
    def __init__(self, services={}):
        self.name = 'HTTPLogger Addon, by Marco Urbano'
        self.version = '1.1'
        self.services = services

    # Uncomment if is needed to trigger some event when a request is intercepted.
    #def request(self, flow):
    #   print("request received.")

    # When handling a response we need to read not only the headers, but most importantly we
    # need to read the content of the message (the html page) because we need to observe what changes
    # take place (e.g. when an XSS exploit is used we need to read what is the content of the web page that
    # is vulnerable).
    def response(self, flow):
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
            data_folder = Path("../http_dataset/")
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

