#! /usr/bin/python

"""
    
"""

import sys # sys.argv
from time import sleep
import SimpleCV # .Camera
import subprocess
import tempfile


print "Hello from self_contained.py"

# Constants
MOAR = 4. # multiplier on the user's x displacement from center
CAMERA_ID = 0 # replace with the camera id of your webcam
DELAY_SECONDS = 0.
X_CAM_LEFT = 1.
X_CAM_RIGHT = -1.

# Sampling resolution
SAMPLING_Y_STEP = 8 # pixels
SAMPLING_X_STEP = 8 # pixels


RAW_APPLESCRIPT = """
tell application "System Preferences"
    activate
    reveal anchor "output" of pane id "com.apple.preference.sound"
end tell

tell application "System Events"
    tell slider 1 of group 1 of tab group 1 of window 1 of process "System Preferences"
        set value to BALANCE
    end tell
end tell
"""


# init the capture
cam = SimpleCV.Camera(CAMERA_ID)


# shirt
image = cam.getImage()
(width, height) = image.size()
#
SHIRT_X = int(width * .5)
SHIRT_Y = int(height * .75) # .75 of the way down
#
[SHIRT_R, SHIRT_G, SHIRT_B, _] = image.getPixel(SHIRT_X, SHIRT_Y)
print image.getPixel(SHIRT_X, SHIRT_Y)

#
COLOR_TOLERANCE = 40 # TODO adjust
#
MIN_R = SHIRT_R - COLOR_TOLERANCE
MIN_G = SHIRT_G - COLOR_TOLERANCE
MIN_B = SHIRT_B - COLOR_TOLERANCE
#
MAX_R = SHIRT_R + COLOR_TOLERANCE
MAX_G = SHIRT_G + COLOR_TOLERANCE
MAX_B = SHIRT_B + COLOR_TOLERANCE


while True:
    
    sleep(DELAY_SECONDS)

    image = cam.getImage()
    if image is not None:

        (width, height) = image.size()

        vote_sum = width / 2.
        n_votes = 1

        for y in range(0, height, SAMPLING_Y_STEP):

            row = image.getHorzScanline(y)

            for x in range(0, width, SAMPLING_X_STEP):

                [r, g, b] = row[x]
            
                if r > MIN_R and g > MIN_G and b > MIN_B:
                    if r < MAX_R and g < MAX_G and b < MAX_B:
                    
                        vote_sum += x
                        n_votes += 1

        user_x = vote_sum / n_votes

        # print n_votes # probably want in the range of 50-200. adjust COLOR_TOLERANCE

        percent_rightward = float(user_x) / width

        # multiply x displacement from center by a constant MOAR > 1.
        percent_rightward -= 0.5
        percent_rightward *= MOAR
        percent_rightward += 0.5

        if percent_rightward < 0.:
            percent_rightward = 0.

        if percent_rightward > 1.:
            percent_rightward = 1.
        
        # rescale into units where -1. is far left (from user's POV) and 1. is far right
        user_x = X_CAM_LEFT + percent_rightward * (X_CAM_RIGHT - X_CAM_LEFT)
        
        balance = user_x

        #
        ### like doing #define BALANCE (balance)
        #
        # (for some reason I could'nt get str.replace to work so I re-implemented it)

        replace_me = 'BALANCE'

        raw_applescript_2 = RAW_APPLESCRIPT
    
        loc = raw_applescript_2.find(replace_me)

        loc_after = loc + len(replace_me)

        half_1 = raw_applescript_2[0:loc]
        half_2 = raw_applescript_2[loc_after:]

        raw_applescript_3 = half_1 + str(balance) + half_2

        # dump to a file
        code_file_name = ''

        with tempfile.NamedTemporaryFile(suffix='.txt', mode='w', delete=False) as f:
            f.write(raw_applescript_3)
            code_file_name = f.name
    
        # here goes...
        subprocess.call(['osascript', code_file_name])

        # clean up
        subprocess.call(['rm', code_file_name])

