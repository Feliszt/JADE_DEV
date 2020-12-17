#
#   installation_sensor_dummy.py
#
#   This script emulates the output of "installation_sensor.py"
#   without having to be plugged to an actual load sensor.
#   This is useful for testing and is run during the installation
#   when we are facing technical issues with the sensor.
#

# osc client
from pythonosc import udp_client
# misc
import os
import json
import time
import random

# init folders name for data
config_folder = "../DATA/config/"

# get script name
program_name = os.path.basename(__file__)

# debug
base_debug = "[{}]\t".format(program_name)
print("{}start.".format(base_debug))

# load calibration
with open(config_folder + 'calib.json', 'r') as f_calib:
    calib = json.load(f_calib)
    
# load calibration
with open(config_folder + 'config.json', 'r') as f_config:
    config = json.load(f_config)

# init list of objects
objects_on_scale = []

# setup OSC
osc_client = udp_client.SimpleUDPClient(config["osc_addr"], config["osc_port"])

# loop that imitates adding and removing elements on scale
while True :

    # randomly decide to remove or add element
    if random.random() < 0.2 :
        # add element
        if random.random() < 0.4 :
            object_to_add = random.choice(calib["objects"])
            if object_to_add["name"] not in objects_on_scale :
                objects_on_scale.append(object_to_add["name"])
                osc_client.send_message("/add", object_to_add["name"])
        # remove element
        else:
            if len(objects_on_scale) > 0 :
                object_to_remove = random.choice(objects_on_scale)
                objects_on_scale.remove(object_to_remove)
                osc_client.send_message("/remove", object_to_remove)

    #
    print(objects_on_scale)

    # sleep
    time.sleep(2)
