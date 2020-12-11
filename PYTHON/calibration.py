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

# save a level
def save_level(event):

    # check state
    if state == -1 :
        print("{}Too soon to save level. Wait for analysis window to have enough samples.".format(base_debug))
        return
    if state == 0 :
        print("{}Can't save zero level.".format(base_debug))
        return
    if state == 1 :
        print("{}Can't save level. Too much instability.".format(base_debug))
        return

    # compute absolute difference between this level and zero
    level_weight = int(abs(zero - weight_mean))

    # update nb_objects
    nb_objects = len(calib["objects"])

    # save to json
    object = {}
    object["weight"] = level_weight
    object["name"] = "object #" + str(nb_objects + 1)
    calib["objects"].append(object)

    # update calibration file
    with open(config_folder + 'calib.json', 'w') as f_calib:
        # write file
        json.dump(calib, f_calib)

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

# set up matplotlib window
fig = plt.figure(2, figsize=(7, 7))
cid = fig.canvas.mpl_connect('button_press_event', save_level)

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

        # compute distance to zero
        dist_to_zero = abs(weight_mean - zero)

        ## detect state
        ## 3 states possible : at zero / changing / at level
        if dist_to_zero <= config["sensitivity_from_levels"]:
            state = 0
        else :
            if weight_dev > config["flatness_sensitivity"] :
                state = 1
            else :
                state = 2

        # debug
        #print("{}value = {}\tmean = {}\tdev = {}".format(base_debug, int(curr_weight), int(weight_mean), int(weight_dev)))

    # set graph color
    graph_color = 'gray'
    if state == 0 :
        graph_color = 'blue'
    if state == 1 :
        graph_color = 'red'
    if state == 2 :
        graph_color = 'green'

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


#plt.show()
