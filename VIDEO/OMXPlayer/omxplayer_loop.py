import subprocess
import time
import json
import os

# set files and folder
play_file = "../../DATA/config/play.json"
video_folder = "../../DATA/videos/placeholders/"
video_files = [video_folder + file for file in os.listdir(video_folder)]


#
file_ind = 0
while True :
    with open(play_file, 'r') as f :
        data = json.load(f)
        play_state = data["play"]

    #
    if play_state :
        subprocess.call(["omxplayer", video_files[file_ind]])
        
        # update file index
        file_ind += 1
        if file_ind == len(video_files) :
            file_ind = 0
    else :    
        time.sleep(1)