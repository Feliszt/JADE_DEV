#
#   calibration_videos_duration.py
#
#   This script is run last during calibration. calibration_object.py
#   will be run before, and then the corresponding videos will be
#   provided in calib.json. Once this is all done, this script
#   simply runs through the list of videos and runs a ffprobe to get
#   their durations
#

# misc
import os
import json
import subprocess

# this function returns the duration in second of a video
def get_duration(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

# get script name
program_name = os.path.basename(__file__)

# debug
base_debug = "[{}]\t".format(program_name)
print("{}start.".format(base_debug))

# init folders name for data
config_folder = "../DATA/config/"

# load config
with open(config_folder + 'config.json', 'r') as f_config:
    config = json.load(f_config)

# load calib
with open(config_folder + 'calib.json', 'r') as f_calib:
    calib = json.load(f_calib)

# set video folder
video_folder = "../DATA/videos/" + config["video_folder"] + "/"

# loop through all previously calibrated objects in json
objects = []
for object in calib["objects"] :
    # get full path of video and duration
    video_path = video_folder + object["video_name"] + ".mp4"
    video_duration = get_duration(video_path)

    # add it to object
    object["video_duration"] = video_duration
    objects.append(object)

    # debug
    print("{}[{}]\t{} sec".format(base_debug, video_path, video_duration))

# do the same for base_video
base_video_path = video_folder + calib["base_video"]["video_name"] + ".mp4"
base_video_duration = get_duration(base_video_path)

# debug
print("{}[{}]\t{} sec".format(base_debug, base_video_path, base_video_duration))

# update calib object
calib["objects"] = objects
calib["base_video"]["video_duration"] = base_video_duration

# write file
with open(config_folder + 'calib.json', 'w') as f_calib:
    json.dump(calib, f_calib)
