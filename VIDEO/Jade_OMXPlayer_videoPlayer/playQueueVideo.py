
import os
import time
from omxplayer.player import OMXPlayer

# get data folder
video_folder = "../../DATA/videos/placeholders/"

# get files
files = [video_folder + f for f in os.listdir(video_folder)]
video1 = video_folder + "video08_7.mp4"
video2 = video_folder + "video09_3.mp4"


#
#print(files[0])

player1 = OMXPlayer(video1, dbus_name = 'org.mpris.MediaPlayer2.omxplayer1')
player2 = OMXPlayer(video2, dbus_name = 'org.mpris.MediaPlayer2.omxplayer2')
