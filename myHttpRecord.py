# Author: Marco Urbano.
# Date: 14 January 2021.
# Description: myHttpRecord is a simple object that can be used both for the request and response
#              to store headers and content intercepted by mitmproxy and to return a JSON object to be saved.
# Notes:
#           - The idea to create a class with a method that make JSONable a complex object was found there:
#               https://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable/15538391
#           - Other interesting tips:
#               * https://github.com/simplejson/simplejson/issues/52#issuecomment-23667961

import json


class MyHttpRecord:
    def __init__(self):
        # Request data
        self.req_headers: dict = {}
        self.req_content: str = ""
        # Response data
        self.res_headers: dict = {}
        self.res_content: str = ""

        # Initialize here any other data that is not present so far. (e.g. pretty url as in
        # commit b2772da5fd540c0b9d1dc07ce4a4a9606147fe3e)
        self.pretty_url = ""

    def __init__(self, req_headers, req_content, res_headers, res_content, pretty_url=""):
        self.req_headers = req_headers
        self.req_content = req_content
        self.res_headers = res_headers
        self.res_content = res_content
        self.pretty_url = pretty_url

    # Returns the serialized JSON of self.
    def getJSON(self):
        # Building an on-the-fly dictionary to make this object JSON serializable.
        dictRecord = {  "Url": self.pretty_url,
                        "Request": {"Headers": self.req_headers, "Content": self.req_content},
                        "Response": {"Headers": self.res_headers, "Content": self.res_content}
                     }
        # Passing the dictionary built on the fly because it is serializable.
        return json.dumps(dictRecord, indent=2)
