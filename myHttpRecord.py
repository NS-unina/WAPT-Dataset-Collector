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

# to extract parameters from a POST Request.
import urllib.parse
import mitmproxy.net.http.url

class MyHttpRecord:
    def __init__(self):
        # --------- REQUEST DATA ---------------
        self.req_headers: dict
        self.req_content: str

        # Response data
        self.res_headers: dict
        self.res_content: str

        # Initialize here any other data that is not present so far. (e.g. pretty url as in
        # commit b2772da5fd540c0b9d1dc07ce4a4a9606147fe3e)
        self.pretty_url = ""

    def __init__(self, flow):

        # --------- REQUEST DATA ---------------
        # use .decode() on content to get the webcontent decoded. (mitmproxy saves it as Bytes)
        self.req_headers = dict(flow.request.headers.items())
        self.req_content = str(flow.request.content.decode())

        """
            ISSUE 16/01/21: when the intercepted request method is POST the parameters are returned into the
                            flow.request.content field with the form:
                            
                                            param1=param1_content
                            
                            this string must be managed to be converted as dict, just as the case of a GET request.
                            
        """
        #if flow.request.method == "POST":
        #    self.req_param = tuple((str(flow.request.content.decode())).replace('=', ':'))
        #else:

        # get request parameters (mitmproxy gets it as tuple)
        self.req_param = flow.request._get_query()

        # --------- RESPONSE DATA ---------------
        # use .decode() on content to get the webcontent decoded. (mitmproxy saves it as Bytes)
        self.res_headers = dict(flow.response.headers.items())
        self.res_content = str(flow.response.content.decode())

        # --------- OTHER FLOW DATA ---------------
        self.pretty_url = flow.request.pretty_url

    # Returns the serialized JSON of self.
    def getJSON(self):
        # Building an on-the-fly dictionary to make this object JSON serializable.
        dictRecord = {
                        "Url": self.pretty_url,
                        "Request": {"Headers": self.req_headers, "Content": self.req_content, "Parameters": dict(self.req_param)},
                        "Response": {"Headers": self.res_headers, "Content": self.res_content}
                     }
        # Passing the dictionary built on the fly because it is serializable.
        return json.dumps(dictRecord, indent=2)
