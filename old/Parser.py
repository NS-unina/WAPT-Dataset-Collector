# Author: Marco Urbano.
# Date: 12 January 2021.
# Description: this file contains the class myParser, a subclass of HTMLParser, used to get the title from
#              the http response intercepted by mitmproxy.
# Notes:       none


# html.parser library will be employed to extract the title from the http response received.
# The aim of employing it is to save the recorded http response with the title of the page
# plus the datetime.
from html.parser import HTMLParser

class Parser(HTMLParser):


    def __init__(self):
        # Call to super to execute the superclass constructor.
        super().__init__()
        # Reset the instance. Loses all unprocessed data. This is called implicitly at instantiation time.
        self.reset()
        # Variables with _name have been explicitly made private.
        # Initializing the boolean attribute that shows if the current tag is "title" to False.
        self.handling_title = False
        # Initializing the string that corrisponds to the title to ''
        self.title = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.handling_title = True

    def handle_data(self, data):
        if self.handling_title:
            self.title = data
            print(self.title)
            self.handling_title = False

    def get_title(self):
        # Getter for _title private attribute.
        return self.title
