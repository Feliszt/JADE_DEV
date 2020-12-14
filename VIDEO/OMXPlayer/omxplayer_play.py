# misc
import subprocess
import time


# set video file
video_folder = "../../DATA/videos/placeholders/"
video_file01 = video_folder + "base_video.mp4"
video_file02 = video_folder + "etain_video.mp4"

# play video
subprocess.call(["omxplayer", video_file01])
subprocess.call(["omxplayer", video_file02])
subprocess.call(["omxplayer", video_file01])
