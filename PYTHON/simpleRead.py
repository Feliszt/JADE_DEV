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

    # get info
    weight_mean = np.mean(weight_array_small)
    weight_dev = np.std(weight_array_small)
    weight_diff = prev_weight - curr_weight

    # debug
    print("current value = {}\tmean = {}\tdev = {}\tdiff = {}".format(int(curr_weight), int(weight_mean), int(weight_dev), int(weight_diff)))

    # plot
    plt.clf()
    plt.plot(weight_array_big, 'b')
    plt.pause(0.05)

    # update variables
    prev_weight = curr_weight
