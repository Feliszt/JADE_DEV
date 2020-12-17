#
#   installation_sensor.py
#
#   This script listens to the OSC adress on which the objects put on and
#   removed from the scale are written.
#   It then plays a dynamic playlist of videos that depends on those objects,
#   the link between each video and the video to play is written in "calib.json".
#   This file is created by running calibration.py
#

# serial communication
import serial
# osc client
from pythonosc import udp_client
# gui
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
# misc
import os
import numpy as np
from sys import platform
import json
import datetime
import time
import subprocess
from itertools import compress

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

# configure python command
python_cmd = "python"
if platform == "linux" or platform == "linux2" :
    python_cmd = "python3"

# debug
base_debug = "[{}]\t".format(program_name)
print("{}start.".format(base_debug))
write_to_log("{}start.".format(base_debug))

# configure serial port
serial_port_name = ""
if platform == "linux" or platform == "linux2" :
    serial_port_name = "/dev/ttyACM0"
elif platform == "win32" :
    serial_port_name = "COM7"

# connect to serial
has_serial = False
serial_tries = 0
while serial_tries < 5 :
    serial_tries += 1
    try :
        ser = serial.Serial(serial_port_name, 57600, timeout=1)
        has_serial = True
        break
    except :
        print("{}Can't access serial port. Try #{}.".format(base_debug, serial_tries))
        write_to_log("{}Can't access serial port. Try #{}.".format(base_debug, serial_tries))
        time.sleep(1)

# check if we managed to connect to serial
if not has_serial :
    print("{}Could not connect to serial. Launching dummy sensor inputs and quitting.".format(base_debug))
    write_to_log("{}Could not connect to serial. Launching dummy and quitting.".format(base_debug))
    subprocess.Popen([python_cmd, "installation_sensor_dummy.py"])
    quit()
else :
    print("{}Connection to serial done.".format(base_debug))
    write_to_log("{}Connection to serial done.".format(base_debug))

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

# setup OSC client
osc_client = udp_client.SimpleUDPClient(config["osc_addr"], config["osc_port"])

# set up matplotlib window
if config["show_plot"]:
    fig = plt.figure(2, figsize=(5, 5))

# loop
loop_incr = 0
error_decode_iter = 0
while True:
    #
    loop_incr += 1

    # get bytes from sensor and decode them
    ser_bytes = ser.readline()
    try :
        decoded_bytes = ser_bytes.decode("utf-8")
        error_decode_iter = 0
    except :
        error_decode_iter += 1
        print("{}ERROR IN DECODE [{}]".format(base_debug, error_decode_iter))
        continue
    decoded_bytes = decoded_bytes.strip()

    if(decoded_bytes == '') :
        continue

    # get measure as float
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
            #print("{}Leaving level [{}]".format(base_debug, weight_mean))

            # save current level
            prev_level = weight_mean

        # detect reaching a level
        if state == 0 and prev_state == 1 :
            # debug
            #print("{}Reaching level [{}]".format(base_debug, weight_mean))

            # get delta from previous level
            level_delta = weight_mean - prev_level
            level_delta_sign = np.sign(level_delta)
            level_delta = abs(level_delta)

            # get distance to all objects and detect object
            dist_to_objects = [abs(level_delta - object["weight"]) for object in calib["objects"]]
            possible_objects_bool = np.array(dist_to_objects) < config["sensitivity_from_levels"]
            possible_objects = list(compress(calib["objects"], possible_objects_bool))
            possible_objects_dist = list(compress(dist_to_objects, possible_objects_bool))
            possible_objects_all = [(object, dist) for object, dist in zip(possible_objects, possible_objects_dist)]
            possible_objects_all.sort(key=lambda x:x[1])

            #print("{}{}".format(base_debug, possible_objects_all))

            # if we found a match, we either remove it or add it to the list
            if len(possible_objects) > 0 :
                if level_delta_sign > 0 :
                    iter = 0
                    while iter < len(possible_objects_all) :
                        if possible_objects_all[iter][0] not in objects_on_board :
                            possible_object = possible_objects_all[iter][0]
                            objects_on_board.append(possible_object)
                            osc_client.send_message("/add", possible_object["name"])
                            #print("{}Adding [{}] on the board.".format(base_debug, possible_object["name"]))
                            break
                        iter += 1
                else :
                    # remove object
                    iter = 0
                    while iter < len(possible_objects_all) :
                        if possible_objects_all[iter][0] in objects_on_board :
                            possible_object = possible_objects_all[iter][0]
                            objects_on_board.remove(possible_objects_all[iter][0])
                            osc_client.send_message("/remove", possible_object["name"])
                            #print("{}Removing [{}] from the board.".format(base_debug, possible_object["name"]))
                            break
                        iter += 1
            # no match! few things can happen
            # multiple objects have been added or removed at the same time
            # or an unknown object has been added or removed
            #else :

            # if current weight is zero, we remove everything
            trust_level = 1.0
            if total_weight < config["sensitivity_from_zero"] :
                for el in objects_on_board :
                    osc_client.send_message("/remove", el["name"])
                objects_on_board = []
            # check trust level
            else:
                total_weight_from_list = 0
                for el in objects_on_board :
                    total_weight_from_list += el["weight"]
                trust_level = abs(total_weight - total_weight_from_list)

            # debug
            objects_on_board_names = [el["name"] for el in objects_on_board]
            print("{}{}".format(base_debug, objects_on_board_names, trust_level))
            print("{}trust = {}".format(base_debug, trust_level))
            write_to_log("{}{}".format(base_debug, objects_on_board_names))

        # update weight
        prev_weight_mean = weight_mean

        # debug
        #print("{}value = {}\tmean = {}\tdev = {}".format(base_debug, int(curr_weight), int(weight_mean), int(weight_dev)))

    # plot curve for debug purposes
    if config["show_plot"]:
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
        plt.axhline(y= zero - config["sensitivity_from_zero"], linestyle = '--', color = 'black', linewidth = 1)
        plt.axhline(y= zero + config["sensitivity_from_zero"], linestyle = '--', color = 'black', linewidth = 1)
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
