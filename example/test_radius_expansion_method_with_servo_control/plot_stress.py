import os
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'STIXGeneral'


plt.figure(1)
#plt.title('Hertz model')  
plt.xlabel('Time / s')  
plt.ylabel(r'$\bar{p}$ / MPa')   
# creat the BTS_peak_points.dat

aim_path_and_name = os.path.join(os.getcwd(), 'stress_tensor_0.txt')

if os.path.isfile(aim_path_and_name):
    X12, Y12 = [], []
    with open(aim_path_and_name, 'r') as stress_strain_data:
        for line in stress_strain_data:
            values = [float(s) for s in line.split()]
            X12.append(values[0])
            Y12.append(values[1] / 1e6)
            #Y12.append(real_porosity)
    
    plt.plot(X12, Y12, 'b-o', label='Measured mean stress', markersize=6, markerfacecolor='none')

plt.axhline(y=0.005, color='r', linestyle='--', label='Target stress')

ax1 = plt.gca()
ax2 = ax1.twinx()
Y13 = []

with open(aim_path_and_name, 'r') as stress_strain_data:
    for line in stress_strain_data:
        values = [float(s) for s in line.split()]
        Y13.append(values[2])

ax2.plot(X12, Y13, 'g->', label='Measured packing density', markersize=6, markerfacecolor='none')
ax2.set_ylabel('Packing density')

ax2.axhline(y=0.635, color='gray', linestyle='--', label='Target packing density')

#ax2.set_ylim([0.6, 0.615])
#plt.xlim([0.00035, 0.0008])
#plt.ylim([0, 0.07])

ax1.tick_params(axis='both', which='major', labelsize=14)
ax2.tick_params(axis='both', which='major', labelsize=14)
ax1.xaxis.label.set_size(16)
ax1.yaxis.label.set_size(16)
ax2.yaxis.label.set_size(16)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=14)

plt.show()