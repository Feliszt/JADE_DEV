import os
import json
import time
import random
from pythonosc import udp_client

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
    
# init list of objects
objects_on_scale = []

# setup OSC
osc_client = udp_client.SimpleUDPClient("127.0.0.1", 8000)
    
# loop that imitates adding and removing elements on scale
while True :
    
    # randomly decide to remove or add element
    if random.random() < 0.5 :
        # add element
        if random.random() < 0.5 :
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