import subprocess
import time
import json

#
play_file = "../../DATA/config/play.json"
video_file = "../../DATA/videos/placeholders/base_video.mp4"

#
while True :
    with open(play_file, 'r') as f :
        data = json.load(f)
        play_state = data["play"]

    print(play_state)
    if play_state :
        subprocess.call(["omxplayer", video_file])