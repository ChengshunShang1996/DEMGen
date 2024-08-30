import os
import numpy as np
import matplotlib.pyplot as plt

levels = np.linspace(0.0,1.000001,100)
#levels = 20

x = []
y = []
z = []
#BTS_peak_points_path_and_name = os.path.join(os.getcwd(),'BTS_peak_points_03_025_001.dat')
BTS_peak_points_path_and_name = os.path.join(os.getcwd(),'porosity_r2mm.txt')
with open(BTS_peak_points_path_and_name, "r") as f_r:
    for line in f_r:
        values = [float(s) for s in line.split()]
        x.append(values[0])
        y.append(values[1])
        z.append(values[2])


#plt.contourf(X, Y, Z, 20, cmap=plt.get_cmap('YlGn'))
#cs = plt.tricontour(x, y, z, levels=levels, colors = 'white', linewidths = 0.1)
#plt.tricontour(x, y, z, levels=[46193, 46195], colors = 'blue', linewidths = 0.5)
plt.tricontourf(x, y, z, levels=levels, cmap='coolwarm')
#cs.clabel(inline=True, fmt='%d', fontsize = 'smaller', manual=true)

plt.xlabel('x')
plt.ylabel('y')
plt.title('Porosity')

plt.xlim((-0.0015, 0.024))
plt.ylim((0, 0.024))

plt.colorbar()
plt.show()