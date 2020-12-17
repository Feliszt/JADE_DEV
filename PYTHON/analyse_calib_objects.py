import json

# get data
with open("../DATA/config/calib.json", "r") as f_calib :
    objects = json.load(f_calib)["objects"]

# get weights
objects_list = [(obj["name"], obj["weight"]) for obj in objects]
objects_list.sort(key=lambda x:x[1])

#
for i in range(0, len(objects_list)) :
    if i > 0 :
        diff = objects_list[i][1] - objects_list[i-1][1]
        print(diff)
    print(objects_list[i])
