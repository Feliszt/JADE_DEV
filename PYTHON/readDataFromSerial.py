import serial
import numpy as np
import matplotlib.pyplot as plt
import time

# configure serial port
ser = serial.Serial('/dev/ttyACM0', 57600, timeout=1)

#
array_size = 1
weight_array = []

# loop
loop_incr = 0
while True:
    #
    loop_incr += 1

    # decode
    ser_bytes = ser.readline()
    decoded_bytes = ser_bytes[0:-2].decode("utf-8")

    if(decoded_bytes == '') :
        continue

    # get measure as flot
    curr_weight = float(decoded_bytes)

    # sliding array
    weight_array.append(curr_weight)
    if(len(weight_array) > array_size):
        weight_array = weight_array[1:]

    # mean
    weight_mean = np.mean(weight_array)
    weight_dev = np.std(weight_array)

    # write to file
    with(open('raw_data.txt', 'a')) as f:
        f.write(str(time.time()) + "\t" + str(curr_weight) + "\n")

    # plot
    #plt.clf()
    #plt.plot(weight_array, 'b')
    #plt.pause(0.05)


    #
    #print("mean = [{}]\tdev = [{}]".format(weight_mean, weight_dev))

#plt.show()
