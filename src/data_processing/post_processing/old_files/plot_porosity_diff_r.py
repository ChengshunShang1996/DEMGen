import numpy as np
import matplotlib.pyplot as plt
import os

x = []
y = []
ytop = []
ybot = []
path_and_name = os.path.join(os.getcwd(),'porosity_diff_radius.txt')
with open(path_and_name, "r") as f_r:
    for line in f_r:
        values = [float(s) for s in line.split()]
        x.append(values[0])
        y.append(values[1])
        ytop.append(values[2])
        ybot.append(values[3])

# This works
plt.errorbar(x, y, yerr=(ybot, ytop), ecolor = 'red', elinewidth = 2, capsize = 4, color = 'gray', marker='o', markersize=3, linestyle="--")


plt.xlabel('Measure radius / m')
plt.ylabel('Porosity')
plt.title('Measured porosity with error bars')

#plt.legend()
plt.show()