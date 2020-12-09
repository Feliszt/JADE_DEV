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
array_size_big = 100
array_size_small = 10
weight_array_big = []
weight_array_small = []

# record variables
data_folder = "../DATA/sensor_data/"
rec_name = "empty"
rec_length = 400  # number of samples in record
rec_delay = 50    # number of data to ignore

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
    weight_array_big.append(curr_weight)
    if(len(weight_array_big) > array_size_big):
        weight_array_big = weight_array_big[1:]

    # store a short window of data
    weight_array_small.append(curr_weight)
    if(len(weight_array_small) > array_size_small):
        weight_array_small = weight_array_small[1:]

    # set plot color
    plot_color = 'r'

    # check if we can record
    if loop_incr >= rec_delay and loop_incr <= (rec_delay + rec_length):
        # debug
        rec_time = loop_incr - rec_delay
        print("Recording sample {} / {}".format(rec_time, rec_length))

        # edit color
        plot_color = 'g'

        # save data
        with(open(data_folder + 'rawdata_' + rec_name + '.txt', 'a')) as f:
            f.write(str(curr_weight) + "\n")

    # plot
    plt.clf()
    plt.plot(weight_array_big, plot_color)
    plt.pause(0.05)

#plt.show()
