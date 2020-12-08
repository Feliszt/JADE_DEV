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
array_size_small = 10
weight_array_big = []
weight_array_small = []

# init detection variables
dev_threshold = 40
prev_level = False

# levels
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

    # get measure as flot
    curr_weight = float(decoded_bytes)

    # store a big window of data
    weight_array_big.append(curr_weight)
    if(len(weight_array_big) > array_size_big):
        weight_array_big = weight_array_big[1:]

    # store a short window of data
    weight_array_small.append(curr_weight)
    if(len(weight_array_small) > array_size_small):
        weight_array_small = weight_array_small[1:]

    # mean
    weight_mean = np.mean(weight_array_small)
    weight_dev = np.std(weight_array_small)

    # get if plateau or not
    is_level = (weight_dev < 40)

    # detect going to a new level
    if(is_level and not prev_level) :
        # get current level
        current_level_detected = weight_mean

        # compare with all known levels
        level_probs = np.absolute(1 - np.array(level_values) / current_level_detected)
        detected_level = np.argmin(level_probs)

        # debug
        print("New object detected -> [{}]".format(level_names[detected_level]))

    #if(is_level) :
        #print("Currently at level [{}]".format(current_level_detected))

    # get difference from previous weight
    diff_weight = prev_weight - curr_weight

    # write to file
    #with(open('raw_data.txt', 'a')) as f:
    #    f.write(str(time.time()) + "\t" + str(curr_weight) + "\n")

    # plot
    plt.clf()
    plt.plot(weight_array_big, 'b')
    plt.pause(0.05)

    #
    #print("mean = [{}]\tdev = [{}]".format(weight_mean, weight_dev))
    #print("curr value = [{}]".format(diff_weight))

    # update variables
    prev_weight = curr_weight
    prev_level = is_level

#plt.show()
