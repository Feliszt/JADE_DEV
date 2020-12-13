#
#   installation_run_all.py
#
#   This script is launched at launch and runs the 2 scripts necessary for
#   the Jade installation by Chloé Devanne.
#   script 1 : installation_sensor.py, which receives data from sensor, analyze it
#   and sends activity on scale to 2nd script
#   script 2 : installation_play_video_queue.py, which plays an infinite loop of
#   videos depending on what's on the scale
#

# misc
import os
import subprocess
from sys import platform
import time
import json

# get script name
program_name = os.path.basename(__file__)

# debug
base_debug = "[{}]\t".format(program_name)
print("{}start.".format(base_debug))

# set python command
python_cmd = "python"
if platform == "linux" or platform == "linux2" :
    python_cmd = "python3"
    
# init folders name for data
config_folder = "../DATA/config/"

# load config
with open(config_folder + 'config.json', 'r') as f_config:
    config = json.load(f_config)

# run script 1
if config["run_sensor"] :
    subprocess.Popen([python_cmd, "installation_sensor.py"])

# run script 2
if config["run_video"] :
    subprocess.Popen([python_cmd, "installation_play_video.py"])

# run loop forever to catch keyboard interrupts
while True :
    time.sleep(1)
