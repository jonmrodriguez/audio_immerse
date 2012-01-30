#! /usr/bin/python


"""
immersive_audio

Usage:
immersive_audio
"""


import os

# first arg is camera id. 0 means iSight webcam
# next four args are left x, right x, top y, bottom y. left-right from cam's POV
# last arg is the outputting callback
os.system('track_faces 0 .1 1. -1. 1. -1. volume_balance')

