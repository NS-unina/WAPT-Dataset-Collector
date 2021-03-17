# Author: Marco Urbano.
# Date: 14 March 2021.
# Description: Session class represents a recording session. It contains both http transactions and action chain
#              recorded on the end client.
# Notes:
#       I've not written the default constructor because it would have resulted in a code duplication, instead
#       I've preferred to write one constructor that takes in input all the attributes but with default values.
#                                                                                               Marco, 14/03/21
#

# to save attribute named "start_time".
from datetime import datetime

from HTTPRecord import *

# Used to save files specifying the path (a directory that differs from the cwd)
from pathlib import Path

# Initially used to invoke "mkdir" to create the dataset folder.
import os
import errno


class Session:
    def __init__(self, url="", task_name="", start_time=None, http_transactions=[],
                 end_user_actions=""):
        self.url: str = url
        self.task_name: str = task_name
        self.start_time: datetime = start_time
        #self.end_time: datetime = None

        # TODO: Dataset path will be obtained later from task_name, there is no sense to put it as an attribute.
        # self.dataset_path: str = dataset_path

        # contains the list of HTTPRecord objects.
        self.http_transactions: list = http_transactions
        # the JSON object that will be received at the end of the recording session.
        self.end_user_actions: str = end_user_actions

    def saveSession(self):
        # here the code for saving both http_transactions and end_user_actions in the proper folder.

        # replacing all white space with underscores to avoid problems when making the directory named as the task.
        self.task_name = self.task_name.replace(" ", "_")
        # data_folder will be located outside of the current folder (named src/). It will be named as the task that
        # we're currently recording. Every record related to the same task will be saved under the same parent folder.
        out_folder = Path("../out/" + self.task_name + "/" + str(self.start_time).replace(" ", "_"))

        # Every intercepted request will be labeled with the name of the resource requested
        # plus the current datetime (YYYY-MM-DD HH:MM:SS.DS).
        #current_filename = '' + '.json'
        #file_to_open = dataset_folder / current_filename


        # Save each recorded http transaction with an integer only to take trace of which has happened first.
        trans_n = 1
        for transaction in self.http_transactions:
            output = str(trans_n) + '.json'
            trans_rec = out_folder / output

            # Create the directory named as the current task with the first usage.
            if not os.path.exists(os.path.dirname(trans_rec)):
                try:
                    os.makedirs(os.path.dirname(trans_rec))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            # Just a little syntaptic sugar: could be written without the "with ... as ..."
            # but doing this way the opened file will be closed after the manipulation.
            with open(trans_rec, "w") as record_1:
                # write the http_transaction as JSON.
                record_1.write(transaction.getJSON())

            trans_n += 1

        # Save the file that contains the chain of actions performed by the user
        u_actions_rec = out_folder / "end_user_actions.json"
        with open(u_actions_rec, "w") as record_2:
            record_2.write(self.end_user_actions)
