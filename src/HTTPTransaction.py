# Author: Marco Urbano.
# Date: 14 January 2021.
# Description: HTTPTransaction is a simple object that can be used both for the request and response
#              to store headers and content intercepted by mitmproxy and to return a JSON object to be saved.
# Notes:
#           - The idea to create a class with a method that make JSONable a complex object was found here:
#               https://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable/15538391
#           - Other interesting tips:
#               * https://github.com/simplejson/simplejson/issues/52#issuecomment-23667961

import json

# to extract parameters from a POST Request.
import urllib.parse
import mitmproxy.net.http.url

# to obtain name using gethostbyaddr
import socket

class HTTPTransaction:
    def __init__(self):
        # --------- REQUEST DATA ---------------
        self.req_headers: dict
        self.req_content: str
        self.req_param: dict
        # Response data
        self.res_headers: dict
        self.res_content: str

        # Initialize here any other data that is not present so far. (e.g. pretty url as in
        # commit b2772da5fd540c0b9d1dc07ce4a4a9606147fe3e)
        self.pretty_url = ""

        # The following attribute will be employed by HTTPLogger when writing data on the output folder.
        self.time_intercepted = None
    # services is the dict in the HTTPLogger constructor, it contains info about the host on the network.
    def __init__(self, flow, services):

        # --------- REQUEST DATA ---------------
        # use .decode() on content to get the webcontent decoded. (mitmproxy saves it as Bytes)
        self.req_headers = dict(flow.request.headers.items())
        self.req_content = str(flow.request.content.decode())

        """
            mitmproxy treats differently GET and POST requests. 
            
            The first ones will have their own parameters contained into the URL and to get them you will only
            need to call the query() method from Request class.
            
            The latter ones will have their own parameters contained into the 'content' field of the same class.
            To extract the parameters contained into a POST request you need to call the urlencoded_form() method
            that returns a MultiDictView object. Finally this needs to be converted as a dict to be serialized as
            JSON.
        """
        if flow.request.method == "POST":
            # urlencoded_form returns a MultiDictView object.
            self.req_param = dict(flow.request.urlencoded_form)
        else:
            # _get_query returns a tuple.
            self.req_param = dict(flow.request.query)

        # --------- RESPONSE DATA ---------------
        # use .decode() on content to get the webcontent decoded. (mitmproxy saves it as Bytes)
        self.res_headers = dict(flow.response.headers.items())
        self.res_content = str(flow.response.content.decode())

        # --------- OTHER FLOW DATA ---------------
        self.pretty_url = flow.request.pretty_url

        # the IP Address of the client that does the request.
        # this object has the following form:
        # <ClientConnection: IP:PORT>
        # https://discourse.mitmproxy.org/t/3-0-flow-client-conn-ip-address-returns-something-different-than-before/777/2
        # Further more, ip_address is still a tuple (look in connections.py) that has the same form of ClientConnection.
        self.client_ip = str(flow.client_conn.ip_address[0])
        self.client_port = str(flow.client_conn.ip_address[1])
        # client name will always be already known to the interceptor (it queryes the DNS when intercepting the request)
        self.client_name = services[self.client_ip]




    # Returns the serialized JSON of self.
    def get_dict(self):
        # Building an on-the-fly dictionary to make this object JSON serializable.
        dict_record = {
                        "url": self.pretty_url,
                        "request": { "client": {"ip address": self.client_ip, "port": self.client_port,
                                                "name": self.client_name},
                                     "headers": self.req_headers, "content": self.req_content, "parameters": self.req_param},
                        "response": {"headers": self.res_headers, "content": self.res_content}
                     }
        # Passing the dictionary built on the fly because it is serializable.
        #return json.dumps(dict_record, indent=2)
        return dict_record
