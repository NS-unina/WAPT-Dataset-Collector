# Author: Marco Urbano.
# Date: 29 March 2021.
# Description: this script performs the replay of the recorded session by means of Player class.
# Notes:
#       Not so much to say about this script, it only performs a arguments check and instantiates a Player.

# Command line argument parser.
import argparse

# Player class.
from Player import *

# delegate parsing task to argparse library.
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-recording", "--recording", default='null',
                        help="recording must contain the name of the file that contain the recording to reproduce."
                             + "WAPT-Dataset-Collector saves recording files in out/ folder.")
args = arg_parser.parse_args()

# dictionary that contains the JSON file r
record_dict = {}
# proceed only if -recording is not null, a recording to be reproduced must be provided.
if args.recording != 'null':
    # TODO: implement following Player methods.
    player = Player(args.recording)
    player.replay_actions()
else:
    print("Error! You need to provide the path to the recording to replay!\n")





