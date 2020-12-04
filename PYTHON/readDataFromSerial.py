import serial

# configure serial port
ser = serial.Serial('COM7', 57600, timeout=1)

# loop
while True:
    # decode
    ser_bytes = ser.readline()
    decoded_bytes = ser_bytes[0:-2].decode("utf-8")

    if(decoded_bytes == '') :
        continue

    # get measure as flot
    curr_weight = float(decoded_bytes)

    # debug
    print(curr_weight)
