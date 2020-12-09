import serial
import numpy as np
import matplotlib.pyplot as plt
import time
from sys import platform

# configure serial port
serial_port_name = ""
if platform == "linux" or platform == "linux2" :
    serial_port_name = "/dev/ttyACM0"
elif platform == "win32" :
    serial_port_name = "COM7"
ser = serial.Serial(serial_port_name, 57600, timeout=1)

# init arrays
array_size_big = 500
array_size_small = 20
weight_array_big = []
weight_array_small = []

# init stat variables
weight_mean = -1
weight_dev = -1

# init detection variables
start_analyze = 20
dev_threshold = 200
prev_level = False

# levels
current_level = 0
level_values = [396351, 416152, 422641]
level_names = ["VIDE", "METRE", "ETAIN"]

# loop
loop_incr = 0
prev_weight = 0
while True:
    #
    loop_incr += 1

    # decode
    ser_bytes = ser.readline()
    decoded_bytes = ser_bytes.decode("utf-8")
    decoded_bytes = decoded_bytes.strip()

    if(decoded_bytes == '') :
        continue

    # get bool if analyze is possible
    can_analyze = loop_incr > start_analyze

    if(not can_analyze) :
        continue

    # get measure as flot
    curr_weight = float(decoded_bytes)

    # store a big window of data
    weight_array_big.append(curr_weight)
    if(len(weight_array_big) > array_size_big):
        weight_array_big = weight_array_big[1:]

    # store previous weight mean
    if(len(weight_array_small) > 1) :
        weight_mean_prev = np.mean(weight_array_small)

    # store a short window of data
    weight_array_small.append(curr_weight)
    if(len(weight_array_small) > array_size_small):
        weight_array_small = weight_array_small[1:]

    # compute mean and dev
    if(len(weight_array_small) > 1) :
        weight_mean = np.mean(weight_array_small)
        weight_dev = np.std(weight_array_small)

    # get if plateau or not
    is_level = (weight_dev < dev_threshold)

    # we were on a plateau and we are leaving it
    if(can_analyze and not is_level and prev_level) :
        # update current level in case of drift
        current_level = weight_mean_prev

        # debug
        print("[LEAVING PALIER]\tlevel = {}".format(current_level))

    # we just reached a plateau
    if(can_analyze and is_level and not prev_level) :
        # get current level
        prev_level = current_level
        current_level = weight_mean

        # get direction of change and delta
        sign_level = np.sign(current_level - prev_level)
        delta_level = abs(current_level - prev_level)

        # debug
        print("[REACHING PALIER]\tlevel = {}\tsign = {}\tdelta = {}".format(current_level, sign_level, delta_level))

        # compare with all known levels
        level_probs = np.absolute(1 - np.array(level_values) / current_level)
        detected_level = np.argmin(level_probs)

        # debug
        #print("New object detected -> [{}]".format(level_names[detected_level]))

    # get difference from previous weight
    diff_weight = prev_weight - curr_weight

    # plot
    plt.clf()
    plt.plot(weight_array_big, 'b')
    plt.pause(0.05)

    # debug
    state = ""
    if(is_level) :
        state = "PALIER"
    #print("current value = {}\tmean = {}\tdev = {}\t{}".format(int(curr_weight), int(weight_mean), int(weight_dev), state))

    # update variables
    prev_weight = curr_weight
    prev_level = is_level

#plt.show()
