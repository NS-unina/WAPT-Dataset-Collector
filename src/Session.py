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

from HTTPTransaction import *

# Used to save files specifying the path (a directory that differs from the cwd)
from pathlib import Path

# Initially used to invoke "mkdir" to create the dataset folder.
import os
import errno

# To make a deep copy of the dictionary containing the action chain.
import copy

class Session:

    def __init__(self, url="", task_name="", start_time=None, http_transactions=[],
                 end_user_actions=""):
        self.url: str = url
        self.task_name: str = task_name
        self.start_time: datetime = start_time
        # self.end_time: datetime = None

        # TODO: Dataset path will be obtained later from task_name, there is no sense to put it as an attribute.
        # self.dataset_path: str = dataset_path

        # contains the list of HTTPTransaction objects.
        self.http_transactions: list = http_transactions
        # the JSON object that will be received at the end of the recording session.
        self.end_user_actions: str = end_user_actions

    def __del__(self):
        del self.url
        del self.task_name
        del self.http_transactions
        del self.end_user_actions

    def save_session(self):
        # here the code for saving both http_transactions and end_user_actions in the proper folder.

        # replacing all white space with underscores to avoid problems when making the directory named as the task.
        self.task_name = self.task_name.replace(" ", "_")
        # data_folder will be located outside of the current folder (named src/). It will be named as the task that
        # we're currently recording. Every record related to the same task will be saved under the same parent folder.
        out_folder = Path("../out/" + self.task_name + "/" + str(self.start_time).replace(" ", "_"))

        # Every intercepted request will be labeled with the name of the resource requested
        # plus the current datetime (YYYY-MM-DD HH:MM:SS.DS).
        # current_filename = '' + '.json'
        # file_to_open = dataset_folder / current_filename

        # Save each recorded http transaction with an integer only to take trace of which has happened first.
        trans_n = 1
        temp_actions_dict = {}
        temp_session_dict = {}

        # Writing the actions performed by the end client together with the http_transaction.
        actions_performed = json.loads(self.end_user_actions)

        # no_actions equals to eua_dict minus 1 because last key represents task name.
        # (could be modified before the release)
        # no_actions = len(eua_dict) - 1

        for transaction in self.http_transactions:

            # action number counter for every http_transaction. It is employed to enumerate actions from a single
            # transaction from 1 to n.
            action_n = 1

            # The action containing JSON uses special actions named "navigateTo" to exactly know when a transaction
            # is beginning. Exploiting this "delimiter" we can extract only values corresponding to actions
            # related to current transaction. delimiter_encountered is a flag employed to know if the delimiter for
            # current transaction has already been met.
            delimiter_encountered = False

            output = str(trans_n) + '.json'
            trans_rec = out_folder / output

            # Create the directory named as the current task with the first usage.
            if not os.path.exists(os.path.dirname(trans_rec)):
                try:
                    os.makedirs(os.path.dirname(trans_rec))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            ''' 
                we're doing a deep copy of the dictinary "actions_performed" because if we would 
                iterate over it by using the method .items() we would not be able to do it because
                we need to modify the dictionary while iterating on it.
            '''
            dict_to_iterate = copy.deepcopy(actions_performed)
            for k, v in dict_to_iterate.items():
                if k != "task_name":
                    if v['action']['type'] == "navigateTo":
                        if not delimiter_encountered:
                            delimiter_encountered = True
                            del actions_performed[k]
                        else:
                            break
                    else:
                        # Copy current key, value pair to the temporary dictionary
                        # that only contains actions belonging to this transaction.
                        temp_actions_dict[action_n] = v
                        del actions_performed[k]
                        action_n += 1
                else:
                    del actions_performed[k]

            # A transaction will contain it own actions aside from http_request and http_response.
            temp_session_dict = transaction.get_dict()
            temp_session_dict["actions"] = dict(temp_actions_dict)


            # Just a little syntaptic sugar: could be written without the "with ... as ..."
            # but doing this way the opened file will be closed after the manipulation.
            with open(trans_rec, "w") as record_1:
                # write the entire session as JSON.
                record_1.write(json.dumps(temp_session_dict, indent=2))

            trans_n += 1

            # Clean temporary dict to make room for next session.
            temp_actions_dict.clear()
            temp_session_dict.clear()

    # This method will be employed to clean current object data structures: the business logic of this script
    # allows only one session per execution, so it is useless to delete and instantiate a new Session
    # everytime the proxy server is asked to start a new session recording.
    def clear(self):
        self.task_name = ""
        self.url = ""
        self.start_time = None
        # Cleaning datastructures employed to save transactions and user actions.
        self.http_transactions.clear()
        # TODO: end_user_action will not be a string anymore with a upcoming update, this line will
        #       be modified to reflect the changes that will occurr to the new data structure employed.
        #       Marco, 20/03
        self.end_user_actions = ""
