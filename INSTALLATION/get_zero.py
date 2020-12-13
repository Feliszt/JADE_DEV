#
#   get_zero.py
#
#   This script perform tar on the load sensor.
#   The scale has to be empty for it to be efficient.
#   It reads the data from the sensor and if it does not
#   deviate past a specified threshold, it stores the mean.
#

# serial communication
import serial
# GUI
import matplotlib.pyplot as plt
# misc
import numpy as np
from sys import platform
import json
import datetime
import os

# get script name
program_name = os.path.basename(__file__)

# debug
base_debug = "[{}]   \t".format(program_name)
print("{}start.".format(base_debug))

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
window_size = config["window_size_zero"]
window = []

# loop
error_decode_iter = 0
loop_incr = 0
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

    # get measure as flot
    curr_weight = float(decoded_bytes)

    # store a big window of data
    window.append(curr_weight)
    if(len(window) > window_size):
        window = window[1:]

    # compute mean and dev
    analysis = ""
    if(len(window) == window_size) :
        weight_mean = np.mean(window)
        weight_dev = np.std(window)

        # debug
        analysis = "mean = {}\tdev = {}\tthresh = {}".format(int(weight_mean), int(weight_dev), config["sensitivity_zero"])
        #print("{}{}".format(base_debug, analysis))

        # if deviation is under a threshold, we consider the data safe and
        # store the result of the mean as the zero
        if(weight_dev <= config["sensitivity_zero"]) :
            # debug
            print("{}Saving zero =  [{}].".format(base_debug, weight_mean))

            # edit calib
            calib["zero"] = int(weight_mean)
            calib["zero_date"] = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            # save zero to calibration file
            with open(config_folder + 'calib.json', 'w') as f_calib:
                # write file
                json.dump(calib, f_calib)

            # quit get_zero app
            print("{}Quitting.".format(base_debug))
            quit()

    # plot curve for debug purposes
    if config["show_plot"]:
        plt.clf()
        plt.plot(window, 'b')
        plt.pause(0.05)