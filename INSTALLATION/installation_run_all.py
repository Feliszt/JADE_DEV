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
import datetime

# init folders name for data
config_folder = "../DATA/config/"
log_folder = "../DATA/log/"

# function that allow writing a log file
def write_to_log(el_to_write) :
    date_str = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    with open(log_folder + "log.txt", 'a') as f_log :
        f_log.write("[" + date_str + "]\t" + el_to_write + "\n")

# get script name
program_name = os.path.basename(__file__)

# debug
base_debug = "[{}]\t".format(program_name)
print("{}start.".format(base_debug))
write_to_log("{}start.".format(base_debug))

# set python command
python_cmd = "python"
if platform == "linux" or platform == "linux2" :
    python_cmd = "python3"

# load config
with open(config_folder + 'config.json', 'r') as f_config:
    config = json.load(f_config)
    
# run zero
if config["perform_zero"] :
    subprocess.call([python_cmd, "get_zero.py"])
    time.sleep(1)
    
#
proc = []

# run sensor script
if config["run_sensor"] :
    proc.append(subprocess.Popen([python_cmd, "installation_sensor.py"]))

time.sleep(1)

# run video script
if config["run_video"] :
    proc.append(subprocess.Popen([python_cmd, "installation_play_video.py"]))
    
# log
write_to_log("{}{} processes. Quitting.".format(base_debug, len(proc)))


while True :
    time.sleep(1)
    

