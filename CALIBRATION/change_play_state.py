import json

json_file = "/home/pi/Projects/JADE_DEV/DATA/config/play.json"

# read
with open(json_file, "r") as f:
    data = json.load(f)
    
#
play_state = data["play"]

# edit
new_data = {}
new_data["play"] = not play_state
print(not play_state)
with open(json_file, "w") as f:
    json.dump(new_data, f)
