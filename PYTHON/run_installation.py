import os
import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from sys import platform
import json
import datetime
import time
import subprocess
from itertools import compress

# get script name
program_name = os.path.basename(__file__)

# debug
base_debug = "[{}]\t".format(program_name)
print("{}start.".format(base_debug))

# run zero
subprocess.call(["python", "get_zero.py"])
time.sleep(1)

# configure serial port
serial_port_name = ""
if platform == "linux" or platform == "linux2" :
    serial_port_name = "/dev/ttyACM0"
elif platform == "win32" :
    serial_port_name = "COM7"
ser = serial.Serial(serial_port_name, 57600, timeout=1)

# init folders name for data
config_folder = "../DATA/config/"

# load config
with open(config_folder + 'config.json', 'r') as f_config:
    config = json.load(f_config)

# load calib
with open(config_folder + 'calib.json', 'r') as f_calib:
    calib = json.load(f_calib)

# init weight windows
big_window_size = config["big_window_size"]
small_window_size = config["small_window_size"]
big_window = []
small_window = []

# fetch zero in calib file
zero = calib["zero"]
prev_level = 0
prev_state = -1
prev_weight_mean = 0

# board state
objects_on_board = []

# set up matplotlib window
fig = plt.figure(2, figsize=(7, 7))

# loop
loop_incr = 0
while True:
    #
    loop_incr += 1

    # decode
    ser_bytes = ser.readline()
    decoded_bytes = ser_bytes.decode("utf-8")
    decoded_bytes = decoded_bytes.strip()

    if(decoded_bytes == '') :
        continue

    # get measure as flot
    curr_weight = float(decoded_bytes)

    # store a big window of data
    big_window.append(curr_weight)
    if(len(big_window) > big_window_size):
        big_window = big_window[1:]

    # store a small window of data for analysis
    small_window = big_window[-small_window_size:]

    # init state
    state = -1      # corresponds to not enough data in buffer

    # compute mean and dev
    if(len(small_window) == small_window_size) :
        # get mean and standard deviation
        weight_mean = np.mean(small_window)
        weight_dev = np.std(small_window)

        # get total weight on board
        total_weight = abs(weight_mean - zero)  # it's supposed to be superior than 0 already

        ## detect state
        ## 2 states possible : [0] at level / [1] changing
        if weight_dev > config["flatness_sensitivity"] :
            state = 1
        else :
            state = 0

        # detect leaving zero or level
        if state == 1 and prev_state == 0 :
            # debug
            print("{}Leaving level".format(base_debug))

            # save current level
            prev_level = weight_mean

        # detect reaching a level
        if state == 0 and prev_state == 1 :
            # debug
            print("{}Reaching level".format(base_debug))

            # get delta from previous level
            level_delta = weight_mean - prev_level
            level_delta_sign = np.sign(level_delta)
            level_delta = abs(level_delta)

            # get distance to all objects and detect object
            dist_to_objects = [abs(level_delta - object["weight"]) for object in calib["objects"]]
            possible_objects = np.array(dist_to_objects) < config["sensitivity_from_levels"]
            possible_objects = list(compress(calib["objects"], possible_objects))

            # if we found a match, we either remove it or add it to the list
            if len(possible_objects) > 0 :
                # remove or add to list
                first_object_name = possible_objects[0]["name"]
                if level_delta_sign > 0 :
                    # add object, but check first if it's not already there
                    if first_object_name not in objects_on_board :
                        objects_on_board.append(first_object_name)
                else :
                    # remove object
                    if first_object_name in objects_on_board :
                        objects_on_board.remove(first_object_name)
            # no match! few things can happen
            # multiple objects have been added or removed at the same time
            # or an unknown object has been added or removed
            #else :

            # if current weight is zero, we remove everything
            if total_weight < config["sensitivity_from_levels"] :
                objects_on_board = []


            # debug
            print(objects_on_board)

        # update weight
        prev_weight_mean = weight_mean

        # debug
        #print("{}value = {}\tmean = {}\tdev = {}".format(base_debug, int(curr_weight), int(weight_mean), int(weight_dev)))

    # set graph color
    graph_color = 'gray'
    if state == 0 :
        graph_color = 'green'
    if state == 1 :
        graph_color = 'red'

    ## plot
    plt.clf()
    # draw big window
    plt.plot(big_window, graph_color, linewidth = 2)
    # draw horizontal line for current zero and sensitivity area
    plt.axhline(y= zero, color = 'black', linewidth = 1)
    plt.axhline(y= zero - config["sensitivity_from_levels"], linestyle = '--', color = 'black', linewidth = 1)
    plt.axhline(y= zero + config["sensitivity_from_levels"], linestyle = '--', color = 'black', linewidth = 1)
    # draw horizontal line for current weight mean
    if state != -1:
        plt.axhline(y = weight_mean, color = 'maroon', linewidth = 1)
        #plt.axhline(y = weight_mean - 3 * weight_dev, linestyle = '--', color = 'maroon', linewidth = 1)
        #plt.axhline(y = weight_mean + 3 * weight_dev, linestyle = '--', color = 'maroon', linewidth = 1)
    # draw vertical line that shows small window
    plt.axvline(x=max(0, len(big_window)-small_window_size), linewidth=1)
    plt.pause(0.05)

    # update state
    prev_state = state

#plt.show()
