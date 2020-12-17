import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack

# data
data_file = "../DATA/sensor_data/rawdata_flaine.txt"

#
weight_data = []

#
with open(data_file, 'r') as f :
    for line in f:
        # get raw data
        raw_data = line.strip()

        # get weight
        weight = raw_data.split("\t")[1]

        # append data
        weight = float(weight)
        weight_data.append(weight)

# compute mean and variation
weight_data_np = np.array(weight_data)
mean = np.mean(weight_data_np)
dev = np.std(weight_data_np)

#
weight_data_norm = 1/(np.max(weight_data_np) - np.min(weight_data_np)) * (weight_data_np - np.min(weight_data_np))

## compute fft
c = """
# Number of samplepoints
N = weight_data_norm.size

# sample spacing
T = 1.0 / 800.0
x = np.linspace(0.0, N*T, N)
y = weight_data_norm
yf = scipy.fftpack.fft(y)
xf = np.linspace(0.0, 1.0/(2.0*T), N//2)

fig, ax = plt.subplots()
ax.plot(xf, 2.0/N * np.abs(yf[:N//2]))
plt.show()
"""

## print mean
print("mean = {}\tvariation = {}".format(mean, dev))

#
n_samples = len(weight_data_np)


plt.plot(weight_data_np[n_samples // 2000 : 2 * n_samples // 2000])
plt.show()
